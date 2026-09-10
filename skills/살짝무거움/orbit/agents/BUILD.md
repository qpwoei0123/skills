# BUILD — 빌드와 배포 재현성

같은 변경이 로컬·CI·배포에서 어떤 입력과 명령으로 결과를 만드는지 본다. [공통 조사 기준](../references/agent-playbook.md)을 함께 따른다.

## 확인할 경로

- manifest scripts, Makefile·task runner와 실제 CI·release 명령
- runtime·toolchain, 작업 디렉터리, 환경변수와 build flag
- cache·volume 선언과 도구가 실제 읽고 쓰는 위치
- 산출물 경로, 이미지 build 단계와 실제 실행 환경

## finding으로 남길 근거

다른 입력이나 실행 경로가 결과물·실패 조건을 바꾸는 근거를 연결한다. 캐시 옵션이나 로그 출력만 다른 경우는 영향이 확인되지 않으면 제외한다.

lint·test·build를 여러 job으로 나눴어도 전체 파이프라인이 같은 검증과 순서를 보장할 수 있다. dev 전용 분기를 production 문제로 확대하지 않는다. 도구 기본 경로는 현재 OS·버전·설정으로 확인한다.

## 범위 조정

CI가 없으면 release script나 문서의 실행법과 실제 명령을 비교한다. 컨테이너가 없으면 해당 조사를 생략하고 사용 중인 toolchain과 배포 경로를 본다. 서로 다른 문제를 `재현성`이라는 큰 제목만으로 한 finding에 합치지 않는다.
