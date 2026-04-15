from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
README_VERSION_RE = re.compile(r"version:\s*([0-9]+\.[0-9]+\.[0-9]+)", re.IGNORECASE)
CHANGELOG_VERSION_RE = re.compile(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\s*$", re.MULTILINE)

QUICKSTART_MARKERS = ("## Quick Start", "## 사용 예시", "## Quickstart")
STRUCTURE_MARKERS = ("## Structure", "## 포함 파일", "## 디렉터리 구조")
TEST_MARKERS = ("## Test", "## 테스트", "## 검증 방법")
OPTIONAL_DIRS = ("agents", "references", "scripts", "assets")

AUTOFIXABLE_ERROR_CODES = {
    "missing_readme",
    "missing_changelog",
    "readme_version_mismatch",
    "readme_missing_quickstart",
    "readme_missing_structure",
    "readme_missing_test",
    "changelog_missing_version_header",
    "changelog_version_mismatch",
    "metadata_version_missing_with_legacy_version",
}


@dataclass
class ValidationMessage:
    code: str
    message: str
    autofixable: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["error_code"] = self.code
        return payload


@dataclass
class SkillReport:
    name: str
    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)

    def add_error(self, code: str, message: str) -> None:
        self.errors.append(
            ValidationMessage(
                code=code,
                message=message,
                autofixable=code in AUTOFIXABLE_ERROR_CODES,
            )
        )

    def add_warning(self, code: str, message: str) -> None:
        self.warnings.append(ValidationMessage(code=code, message=message))

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [warning.to_dict() for warning in self.warnings],
        }


@dataclass
class FrontmatterEntry:
    key: str
    lines: list[str]


@dataclass
class FrontmatterDocument:
    entries: list[FrontmatterEntry]
    body_lines: list[str]


@dataclass
class NormalizeResult:
    skill: str
    blockers: list[ValidationMessage] = field(default_factory=list)
    applied_changes: list[str] = field(default_factory=list)
    remaining_errors: list[ValidationMessage] = field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        return bool(self.blockers)

    @property
    def needs_changes(self) -> bool:
        return bool(self.applied_changes)


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def discover_skills(root: Path) -> list[Path]:
    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / "SKILL.md").exists()
    )


def split_frontmatter_document(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter opening '---'가 없습니다.")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("frontmatter closing '---'가 없습니다.")

    return lines[1:end_index], lines[end_index + 1 :]


def parse_frontmatter_entries(frontmatter_lines: list[str]) -> list[FrontmatterEntry]:
    entries: list[FrontmatterEntry] = []
    current: FrontmatterEntry | None = None

    for raw in frontmatter_lines:
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))

        if indent == 0 and stripped and not stripped.startswith("#") and ":" in stripped:
            if current is not None:
                entries.append(current)
            key = stripped.split(":", 1)[0].strip()
            current = FrontmatterEntry(key=key, lines=[raw])
            continue

        if current is None:
            continue
        current.lines.append(raw)

    if current is not None:
        entries.append(current)

    return entries


def load_frontmatter_document(text: str) -> FrontmatterDocument:
    frontmatter_lines, body_lines = split_frontmatter_document(text)
    entries = parse_frontmatter_entries(frontmatter_lines)
    return FrontmatterDocument(entries=entries, body_lines=body_lines)


def parse_frontmatter(text: str) -> dict[str, object]:
    document = load_frontmatter_document(text)
    data: dict[str, object] = {}

    for entry in document.entries:
        first = entry.lines[0].strip()
        key, value = first.split(":", 1)
        key = key.strip()
        value = value.strip()

        child_values: dict[str, str] = {}
        for child in entry.lines[1:]:
            stripped = child.strip()
            if not stripped or stripped.startswith("#") or ":" not in stripped:
                continue
            child_key, child_value = stripped.split(":", 1)
            child_values[child_key.strip()] = child_value.strip()

        if child_values and value == "":
            data[key] = child_values
        else:
            data[key] = value

    return data


def frontmatter_value(frontmatter: dict[str, object], key: str) -> str:
    value = frontmatter.get(key)
    return value if isinstance(value, str) else ""


def metadata_version(frontmatter: dict[str, object]) -> str:
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get("version")
    return value if isinstance(value, str) else ""


def first_version_header(text: str) -> str:
    match = CHANGELOG_VERSION_RE.search(text)
    return match.group(1) if match else ""


def validate_skill(skill_dir: Path) -> SkillReport:
    report = SkillReport(name=skill_dir.name)

    readme_exists = (skill_dir / "README.md").exists()
    changelog_exists = (skill_dir / "CHANGELOG.md").exists()
    if not readme_exists:
        report.add_error("missing_readme", "필수 파일 누락: README.md")
    if not changelog_exists:
        report.add_error("missing_changelog", "필수 파일 누락: CHANGELOG.md")

    skill_path = skill_dir / "SKILL.md"
    if not skill_path.exists():
        report.add_error("missing_skill_frontmatter", "필수 파일 누락: SKILL.md")
        return report

    skill_text = skill_path.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter(skill_text)
    except ValueError as exc:
        report.add_error("missing_skill_frontmatter", f"SKILL.md frontmatter 오류: {exc}")
        return report

    name = frontmatter_value(frontmatter, "name")
    if not name:
        report.add_error("invalid_name", "frontmatter 필수 키 누락 또는 빈 값: name")
    elif name != skill_dir.name:
        report.add_error(
            "invalid_name",
            f"frontmatter name 불일치: {name} != {skill_dir.name}",
        )

    if not frontmatter_value(frontmatter, "license"):
        report.add_error("missing_license", "frontmatter 필수 키 누락 또는 빈 값: license")

    if not frontmatter_value(frontmatter, "description"):
        report.add_error(
            "missing_description",
            "frontmatter 필수 키 누락 또는 빈 값: description",
        )

    version = metadata_version(frontmatter)
    legacy_version = frontmatter_value(frontmatter, "version")
    if not version:
        if legacy_version:
            report.add_error(
                "metadata_version_missing_with_legacy_version",
                "frontmatter metadata.version이 없고 top-level version만 있습니다.",
            )
            version = legacy_version
        else:
            report.add_error(
                "metadata_version_missing_without_source",
                "frontmatter 필수 키 누락 또는 빈 값: metadata.version",
            )
    elif not SEMVER_RE.match(version):
        report.add_error("invalid_semver", f"metadata.version이 SemVer 형식이 아님: {version}")

    if readme_exists:
        readme_text = (skill_dir / "README.md").read_text(encoding="utf-8")
        version_match = README_VERSION_RE.search(readme_text)
        if not version_match:
            report.add_error("readme_version_mismatch", "README.md에 version 표기가 없습니다.")
        elif version and version_match.group(1) != version:
            report.add_error(
                "readme_version_mismatch",
                f"README.md version 불일치: {version_match.group(1)} != {version}",
            )

        if not contains_any(readme_text, QUICKSTART_MARKERS):
            report.add_error(
                "readme_missing_quickstart",
                "README.md에 Quick Start/사용 예시 섹션이 없습니다.",
            )
        if not contains_any(readme_text, STRUCTURE_MARKERS):
            report.add_error(
                "readme_missing_structure",
                "README.md에 Structure/포함 파일/디렉터리 구조 섹션이 없습니다.",
            )
        if not contains_any(readme_text, TEST_MARKERS):
            report.add_error(
                "readme_missing_test",
                "README.md에 Test/테스트/검증 방법 섹션이 없습니다.",
            )

    if changelog_exists:
        changelog_text = (skill_dir / "CHANGELOG.md").read_text(encoding="utf-8")
        header_version = first_version_header(changelog_text)
        if not header_version:
            report.add_error(
                "changelog_missing_version_header",
                "CHANGELOG.md에 버전 헤더(## x.y.z)가 없습니다.",
            )
        elif version and header_version != version:
            report.add_error(
                "changelog_version_mismatch",
                f"CHANGELOG.md 최신 버전 불일치: {header_version} != {version}",
            )

    for dirname in OPTIONAL_DIRS:
        dir_path = skill_dir / dirname
        if dir_path.exists() and dir_path.is_dir():
            has_files = any(child.is_file() for child in dir_path.rglob("*"))
            if not has_files:
                report.add_warning("empty_optional_dir", f"빈 선택 디렉터리: {dirname}/")

    return report


def render_frontmatter_document(document: FrontmatterDocument) -> str:
    frontmatter_lines: list[str] = []
    for entry in document.entries:
        frontmatter_lines.extend(entry.lines)
    payload_lines = ["---", *frontmatter_lines, "---", *document.body_lines]
    return "\n".join(payload_lines).rstrip() + "\n"


def frontmatter_entry(entries: list[FrontmatterEntry], key: str) -> FrontmatterEntry | None:
    for entry in entries:
        if entry.key == key:
            return entry
    return None


def scalar_value(entry: FrontmatterEntry) -> str:
    first = entry.lines[0].strip()
    if ":" not in first:
        return ""
    return first.split(":", 1)[1].strip()


def metadata_child_map(entry: FrontmatterEntry) -> dict[str, str]:
    children: dict[str, str] = {}
    for child in entry.lines[1:]:
        stripped = child.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        children[key.strip()] = value.strip()
    return children


def upsert_metadata_version(document: FrontmatterDocument) -> tuple[bool, str]:
    entries = document.entries
    legacy_entry = frontmatter_entry(entries, "version")
    metadata_entry = frontmatter_entry(entries, "metadata")
    legacy_value = scalar_value(legacy_entry) if legacy_entry else ""
    metadata_values = metadata_child_map(metadata_entry) if metadata_entry else {}
    current_metadata_version = metadata_values.get("version", "")

    changed = False
    resolved_version = current_metadata_version

    if metadata_entry is None and legacy_value:
        legacy_index = entries.index(legacy_entry) if legacy_entry else len(entries)
        entries.insert(
            legacy_index,
            FrontmatterEntry(key="metadata", lines=["metadata:", f"  version: {legacy_value}"]),
        )
        metadata_entry = entries[legacy_index]
        changed = True
        resolved_version = legacy_value
    elif metadata_entry is not None and not current_metadata_version and legacy_value:
        metadata_entry.lines.append(f"  version: {legacy_value}")
        changed = True
        resolved_version = legacy_value

    if legacy_entry is not None:
        entries.remove(legacy_entry)
        changed = True
        if not resolved_version:
            resolved_version = legacy_value

    return changed, resolved_version


def normalize_readme_content(skill_name: str, version: str, text: str | None = None) -> tuple[str, list[str]]:
    changes: list[str] = []
    if text is None:
        return "", changes

    normalized = text
    version_line = f"`version: {version}`"
    version_match = README_VERSION_RE.search(normalized)
    if version_match:
        current = version_match.group(1)
        if current != version:
            normalized = README_VERSION_RE.sub(f"version: {version}", normalized, count=1)
            changes.append("README.md version 동기화")
    else:
        lines = normalized.splitlines()
        inserted = False
        for index, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(index + 1, "")
                lines.insert(index + 2, version_line)
                inserted = True
                break
        if not inserted:
            lines = [f"# {skill_name}", "", version_line, "", *lines]
        normalized = "\n".join(lines).rstrip() + "\n"
        changes.append("README.md version 추가")

    if not contains_any(normalized, QUICKSTART_MARKERS):
        normalized = normalized.rstrip() + (
            "\n\n## Quick Start\n\n```text\n"
            f"${skill_name}\n"
            "```\n"
        )
        changes.append("README.md Quick Start 섹션 추가")

    if not contains_any(normalized, STRUCTURE_MARKERS):
        normalized = normalized.rstrip() + (
            "\n\n## Structure\n\n```text\n"
            f"{skill_name}/\n"
            "├── SKILL.md\n"
            "├── README.md\n"
            "└── CHANGELOG.md\n"
            "```\n"
        )
        changes.append("README.md Structure 섹션 추가")

    if not contains_any(normalized, TEST_MARKERS):
        normalized = normalized.rstrip() + (
            "\n\n## Test\n\n```bash\n"
            f"python3 scripts/validate_skills.py --skill {skill_name}\n"
            "```\n"
        )
        changes.append("README.md Test 섹션 추가")

    return normalized.rstrip() + "\n", changes


def normalize_changelog_content(version: str, text: str | None = None) -> tuple[str, list[str]]:
    changes: list[str] = []
    if text is None:
        return "", changes

    normalized = text
    match = CHANGELOG_VERSION_RE.search(normalized)
    if match:
        current = match.group(1)
        if current != version:
            normalized = CHANGELOG_VERSION_RE.sub(f"## {version}", normalized, count=1)
            changes.append("CHANGELOG.md 최신 버전 동기화")
    else:
        header = "# Changelog"
        if normalized.strip().startswith(header):
            normalized = normalized.rstrip() + f"\n\n## {version}\n"
        else:
            normalized = f"{header}\n\n## {version}\n\n{normalized.lstrip()}"
        changes.append("CHANGELOG.md 최신 버전 헤더 추가")

    return normalized.rstrip() + "\n", changes


def build_json_payload(reports: list[SkillReport]) -> dict[str, object]:
    error_count = sum(len(report.errors) for report in reports)
    warning_count = sum(len(report.warnings) for report in reports)
    return {
        "skills": [report.to_dict() for report in reports],
        "summary": {
            "skills": len(reports),
            "errors": error_count,
            "warnings": warning_count,
        },
    }


def dumps_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
