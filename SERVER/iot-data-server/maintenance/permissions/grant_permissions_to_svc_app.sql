-- svc_app 계정에 필요한 권한 부여 스크립트
-- svc_dev 계정으로 실행해야 합니다.

-- 1. 현재 연결된 사용자 확인
SELECT current_user, session_user, current_database();

-- 2. svc_app에게 users 테이블 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users TO svc_app;

-- 3. svc_app에게 모든 센서 테이블 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_cds TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_dht TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_flame TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_imu TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_loadcell TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_mq5 TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_mq7 TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_rfid TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_sound TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_tcrt5000 TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_raw_ultrasonic TO svc_app;

-- 4. svc_app에게 Edge 센서 테이블 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_edge_flame TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_edge_pir TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_edge_reed TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sensor_edge_tilt TO svc_app;

-- 5. svc_app에게 액추에이터 테이블 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE actuator_log_buzzer TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE actuator_log_ir_tx TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE actuator_log_relay TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE actuator_log_servo TO svc_app;

-- 6. svc_app에게 기타 테이블 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE devices TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE device_rtc_status TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE alembic_version TO svc_app;

-- 7. 권한 부여 확인
SELECT 
    grantee,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.table_privileges 
WHERE table_schema = 'public'
AND grantee = 'svc_app'
ORDER BY table_name, privilege_type;

-- 8. users 테이블 권한 특별 확인
SELECT 
    grantee,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.table_privileges 
WHERE table_name = 'users' 
AND table_schema = 'public'
AND grantee = 'svc_app'
ORDER BY privilege_type;
