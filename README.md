# phishing-alert-project

GitHub Actions가 매일 오전 9시에 알아서 Render 재배포를 트리거합니다.

  매일 오전 9시
  → GitHub Actions 자동 실행 (본인 PC 꺼져 있어도 됨)
  → Render 재배포
  → 최신 피싱 뉴스 수집
  → 서버 재시작

  workflow_dispatch 옵션은 테스트할 때 수동으로도 실행할 수 있게 추가한 것이고, 평소엔
  건드릴 필요 없습니다.