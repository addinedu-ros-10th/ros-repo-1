std_msgs/Header header
uint8 event_type                # 0: DISPLAY_STARTED, 1: DISPLAY_ENDED, 2: ERROR, 3: CLEARED, 4: PAGE_SWITCHED, 5: ANIMATION_STARTED, 6: ANIMATION_ENDED
uint64 timestamp                # 이벤트 발생 시간
string message                  # 이벤트 메시지

