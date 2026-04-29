# 원격 시드 카탈로그 — GitHub Pages JSON 호스팅

iOS 앱 v1.3.2 이상이 매주 한 번 fetch 하는 동적 콘텐츠 소스.

## 배포 위치

- **공개 URL**: `https://hexisteme.github.io/seeds/remote.json`
- **로컬 staging**: Seed repo `webpages/seeds/`

## 매주 갱신 워크플로 (github MCP)

1. Seed repo `webpages/seeds/remote.json` 의 `seeds` 배열에 새 항목 5-10개 추가.
2. `lastUpdated` 를 ISO 8601 UTC 로 업데이트.
3. Claude (github MCP) 가 `mcp__github__push_files` 로 본 repo `seeds/remote.json` 직접 commit + push.
4. GitHub Pages 자동 배포 (1-2분).
5. iOS 앱이 다음 cold start 시 자동 fetch (24h TTL + 주차 변경 시 강제 refresh).

## 검증

```bash
curl -s https://hexisteme.github.io/seeds/remote.json | jq '.seeds | length'
curl -s https://hexisteme.github.io/seeds/remote.json | jq '.seeds[0]'
```

## JSON 스키마 (v1)

```json
{
  "version": 1,
  "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ",
  "seeds": [
    {
      "id": "UUID 문자열 (대소문자 무관)",
      "domain": "thinking | knowledge | inspiration | reflection | action",
      "format": "read | audio | explore | prompt",
      "title": "한 줄 (24자 이내 권장)",
      "content": "1-3 문장",
      "deepDive": "선택. 2-4 문장 — '더 깊이' 펼침 시 노출",
      "actionPrompt": "선택. 사용자에게 던지는 질문 한 줄",
      "estimatedMinutes": 2-5,
      "source": "선택. 출처 표기 (e.g., 저자, 연도)",
      "tags": ["문자열 배열"],
      "seasonTags": ["spring | summer | fall | winter"],
      "publishedAt": "ISO 8601 UTC",
      "weekId": "YYYY-WNN (ISO 주차)"
    }
  ]
}
```

## 주의사항

- **id 는 영속**: 한번 배포한 시드의 id 는 절대 변경 X (사용자 SeenSeed/FavoritedSeed 가 id 로 추적).
- **forward-compat**: 새 도메인/포맷/시즌 enum 추가는 구버전 앱에서 unknown 으로 skip 됨 (안전).
- **삭제는 주의**: 이미 배포된 시드 삭제 시 사용자 FavoritedSeed 가 nextDueDate 에 매칭 실패 → SR 노출 누락. 가능한 한 삭제 X.
- **콘텐츠 가이드**: 정적 카탈로그 (SeedCatalog.swift) 의 톤·깊이와 일관. 출처 인용 가능하면 source 필드 활용.

## 자동화 (v1.4 검토)

GitHub Action 으로 매주 월요일 자동 트리거 — Claude API 가 도메인 균등하게 5-10개 생성, 자동 PR.
지금은 **수동** — github MCP 페어링.
