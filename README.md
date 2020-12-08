# taxdoc

더빌 사이트에서 납입한 조합비 정보를 PDF 로 다운로드 받을 수 있도록 제공한다.

도커를 통해 쉽게 실행가능하다.

```python
...
## 10080포트, 2020년, 시크릿키=123
docker run -d -p 10080:10080 \
 -e TAX_DOC_KEY=123 \ 
 -e TAX_DOC_YEAR=2020 \ 
 -e TAX_DOC_USER=<더빌 아이디> \
 -e TAX_DOC_PASSWORD=<더빌 암호> \
 -e TAX_DOC_SUB_NAME="공동성명(네이버지회)" \ tost82/taxdoc:v2
```

환경변수 | 필수여부 | 기본값 | 기능
------|------| ---- | ----
TAX_DOC_KEY      | X | 123  | 스크릿키 (마스터 키로도 쓰이므로 변경필수)
TAX_DOC_YEAR     | X | 2019 | 연말정산 귀속년도 
TAX_DOC_USER     | O | 없음  |THE BILL 아이디
TAX_DOC_PASSWORD | O | 없음  |THE BILL 패스워드
TAX_DOC_SUB_NAME | X | 지회명 | 지회이름 (로그인 하단에 노출)
TAX_DOC_FONT     | X | - | 폰트 파일 경로 
TAX_DOC_SIGN     | X | - |사인 파일경로 (직인이 변경될때 수정가능)