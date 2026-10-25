# 본문 이미지 전송

`POST /api/v3/pre-registration/users/email`은 외부 URL 이미지와 CID 인라인 이미지를 지원한다. 두 방식과 기존 `attachments`를 함께 사용할 수 있다.

## 외부 URL

```json
{
  "subject": "모집 안내",
  "html_content": "<img src=\"https://example.com/poster.png\" alt=\"모집 포스터\" style=\"max-width:100%;height:auto;\">"
}
```

서버는 외부 이미지를 다운로드하거나 첨부하지 않는다. 이미지 주소는 인증 없이 접근 가능하고 장기간 유지되어야 한다. 이미지 업로드·호스팅 API는 이번 변경에 포함하지 않는다.

## CID 인라인 이미지

```json
{
  "subject": "모집 안내",
  "html_content": "<p>지원 안내</p><img src=\"cid:poster\" alt=\"모집 포스터\">",
  "inline_images": [
    {
      "content_id": "poster",
      "file_name": "poster.png",
      "content_type": "image/png",
      "content_base64": "<이미지 파일의 Base64 데이터>"
    }
  ]
}
```

- `content_id`: 1~128자. 첫 글자는 영문 또는 숫자, 나머지는 영문·숫자·`_.@-`. 꺾쇠나 `cid:` 접두사를 포함하지 않는다.
- HTML의 `<img src="cid:…">`와 이미지 ID가 일치해야 한다. 중복 ID, 누락된 이미지, 참조되지 않은 이미지는 422로 거절한다.
- HTML을 생략하거나 비워두면 `inline_images` 순서대로 이미지 태그를 자동 생성한다.
- `content`는 선택 사항이며 기본값은 빈 문자열이다. 텍스트·HTML·인라인 이미지가 모두 없으면 422로 거절한다.
- 첨부 및 인라인 이미지 합계 최대 5개, 파일당 최대 1MiB. JPEG, PNG, GIF, WebP를 지원하며 기존 Base64·파일명·시그니처 검증을 적용한다.
- CID는 HTML 파트 아래 `multipart/related`로 포함한다. 일반 첨부파일은 기존 방식으로 유지한다.
- CID 또는 일반 첨부파일이 있으면 OCI Raw Email API, 없으면 기존 HTML 전송 API를 사용한다.
- MIME 직렬화 후 전체 메일 2MiB 제한은 기존과 동일하다. 이 검사는 백그라운드 발송 중 수행되므로 202 접수가 실제 발송 성공을 보장하지 않는다.
- 외부 이미지의 로딩, CID의 첨부 표시, WebP·GIF 렌더링은 수신 메일 앱에 따라 다를 수 있다.

관리자 인증과 수신자 필터, 응답 형식은 기존과 동일하다. 수신 화면의 HTML 미리보기를 구현하는 프런트엔드는 별도의 안전한 렌더링 처리가 필요하다.
