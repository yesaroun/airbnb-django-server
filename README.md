
## 구현 기능

### rooms
rooms/<int:pk>/bookings  
 Get
- 방 예약 리스트
 Post 
- 방 예약 기능
- 날짜 validation 처리

### users

/me  
 Get 
- 로그인한 유저 프로파일 get  
- 본인 계정만 확인 가능
Put
- 로그인한 유저 프로파일 편집

/users  
Post
- 유저 생성

/users/username  
Get 
- 다른 사람 유저 프로필 확인

/users/log-in  
Post
- 로그인

/users/change-password  
Post
- 비밀번호 변경

/users/github  
Post
- github 로그인

## 구현할 기능
reviews : 리뷰 작성을 방을 이용 했던 사람만 가능하도록 하기

