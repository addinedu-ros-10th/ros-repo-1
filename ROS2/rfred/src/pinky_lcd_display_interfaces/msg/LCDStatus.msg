std_msgs/Header header
bool is_active                  # LCD 활성 상태
string current_title            # 현재 타이틀
string[] current_lines         # 현재 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint64 last_update_time         # 마지막 업데이트 시간 (나노초)
uint8 display_mode             # 0: NORMAL, 1: SCROLL, 2: ANIMATION
uint32 error_code               # 에러 코드 (0이면 정상)
string error_message             # 에러 메시지

