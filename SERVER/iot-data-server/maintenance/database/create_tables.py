#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
"""

import asyncio
from app.infrastructure.database import get_db_session

async def create_tables():
    """필요한 테이블들을 생성합니다."""
    async for session in get_db_session():
        try:
            # sensor_edge_flame 테이블 생성
            await session.execute("""
                DROP TABLE IF EXISTS sensor_edge_flame CASCADE;
                CREATE TABLE sensor_edge_flame (
                    time TIMESTAMP WITH TIME ZONE,
                    device_id VARCHAR(64),
                    flame_detected BOOLEAN NOT NULL,
                    confidence NUMERIC,
                    alert_level TEXT,
                    raw_payload JSONB,
                    PRIMARY KEY (time, device_id)
                );
            """)
            
            # sensor_edge_pir 테이블 생성
            await session.execute("""
                DROP TABLE IF EXISTS sensor_edge_pir CASCADE;
                CREATE TABLE sensor_edge_pir (
                    time TIMESTAMP WITH TIME ZONE,
                    device_id VARCHAR(64),
                    motion_detected BOOLEAN NOT NULL,
                    confidence NUMERIC,
                    motion_direction TEXT,
                    motion_speed NUMERIC,
                    processing_time NUMERIC,
                    raw_payload JSONB,
                    PRIMARY KEY (time, device_id)
                );
            """)
            
            # sensor_edge_reed 테이블 생성
            await session.execute("""
                DROP TABLE IF EXISTS sensor_edge_reed CASCADE;
                CREATE TABLE sensor_edge_reed (
                    time TIMESTAMP WITH TIME ZONE,
                    device_id VARCHAR(64),
                    switch_state BOOLEAN NOT NULL,
                    magnetic_field_detected BOOLEAN,
                    raw_payload JSONB,
                    PRIMARY KEY (time, device_id)
                );
            """)
            
            # sensor_edge_tilt 테이블 생성
            await session.execute("""
                DROP TABLE IF EXISTS sensor_edge_tilt CASCADE;
                CREATE TABLE sensor_edge_tilt (
                    time TIMESTAMP WITH TIME ZONE,
                    device_id VARCHAR(64),
                    tilt_detected BOOLEAN NOT NULL,
                    tilt_angle NUMERIC,
                    tilt_direction TEXT,
                    raw_payload JSONB,
                    PRIMARY KEY (time, device_id)
                );
            """)
            
            await session.commit()
            print("✅ 모든 Edge 센서 테이블 생성 완료!")
            break
            
        except Exception as e:
            print(f"❌ 테이블 생성 중 오류: {e}")
            await session.rollback()
            break

if __name__ == "__main__":
    asyncio.run(create_tables()) 