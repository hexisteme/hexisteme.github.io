# 원격 시드 카탈로그 — GitHub Pages JSON 호스팅

iOS 앱 v1.3.2+ 가 fetch 하는 동적 콘텐츠 소스 (24h TTL + 매주 월요일 주차 경계 강제 refresh, 클라가 append+dedupe by id 로 누적 유지).

## 배포 위치

- **공개 URL**: `https://hexisteme.github.io/seeds/remote.json`
- **소스 오브 트루스**: Seed repo(`teme_playground/Seed`) `scripts/seeds_live.csv`(배포 누적본, id 보존) + `scripts/seeds_backlog.csv`(배출 대기 큐)
- 본 repo 의 `seeds/remote.json` 은 **빌드 산출물** — 직접 편집하지 말고 Seed repo 파이프라인으로 재생성.

## 주간 배출 워크플로 (자동 — 2026-07-12 가동)

launchd `com.hexisteme.seed-remote.weekly` 가 **매주 월요일 08:00** 실행 (Mac 꺼져 있었으면 다음 부팅 시 1회 보충, `~/Library/Logs/seed-promote-lastweek` ISO 주차 마커로 멱등):

1. `Seed/scripts/promote_seeds.py --n 5 --push` — 백로그 앞 5개를 누적 CSV 로 승격
2. `build_remote_json.py` 로 누적 CSV **전체 재빌드** → 본 repo `seeds/remote.json` (스키마 검증 실패 시 push 차단)
3. 본 repo commit + push → GitHub Pages 배포 (1-2분)
4. 앱이 월요일 첫 진입 강제 refresh 로 수신

수동 점검: `python3 scripts/promote_seeds.py --dry-run` (repo 무변경). 백로그 runway < 3주면 스크립트가 경고 → 세션에서 신규 생성+적대 루브릭 검수 후 `seeds_backlog.csv` 재적재. 로그: `~/Library/Logs/seed-remote-weekly.log`.

## 검증

```bash
curl -s https://hexisteme.github.io/seeds/remote.json | jq '.seeds | length'
curl -s https://hexisteme.github.io/seeds/remote.json | jq '.seeds[0]'
```

## JSON 스키마 (v2)

```json
{
  "version": 2,
  "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ",
  "seeds": [
    {
      "id": "UUID — CSV 에서 비우면 SHA256(domain|title|content) 로 결정 생성 (앱 Seed.stableID 동일 스킴)",
      "domain": "thinking | knowledge | inspiration | reflection | action",
      "format": "read | audio | explore | prompt",
      "title": "한 줄 (24자 이내 권장)",
      "content": "1-3 문장",
      "deepDive": "선택. 2-4 문장 — '더 깊이' 펼침 시 노출",
      "actionPrompt": "선택. 1탭 이하 무마찰 적용 한 줄",
      "estimatedMinutes": 2,
      "source": "선택. 실제 창시자/대중화자만 (가짜 귀속 금지)",
      "tags": ["문자열 배열"],
      "seasonTags": ["spring | summer | fall | winter"]
    }
  ],
  "retired": ["은퇴시킨 seed id — 정적·원격 양쪽에서 제외됨 (null 가능)"]
}
```

## 주의사항

- **id 는 영속**: 한번 배포한 시드의 id 는 절대 변경 X (사용자 SeenSeed/FavoritedSeed 가 id 로 추적).
- **삭제 대신 retire**: 배포된 시드 삭제 시 FavoritedSeed 의 SR 매칭이 깨짐 → CSV 해당 id 행에 `retired=true` 로 `retired` 목록 배포.
- **전체 재빌드 주의**: 빌드 입력은 반드시 누적본 `seeds_live.csv` — 부분 CSV 로 빌드하면 기존 배포분이 유실됨.
- **forward-compat**: 새 도메인/포맷/시즌 enum 추가는 구버전 앱에서 unknown skip (안전).
- **콘텐츠 가이드**: 무심사 배포이므로 자기규율 필수 — 정적 카탈로그 톤·깊이 일관, 렌즈≠사실, 출처 정직, 하이프 금지, actionPrompt 는 1탭 이하.
