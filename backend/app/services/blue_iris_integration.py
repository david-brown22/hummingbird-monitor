"""
Blue Iris integration service for camera management and webhook handling
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BlueIrisIntegration:
    """Service for integrating with Blue Iris camera system"""
    
    def __init__(self):
        self.base_url = settings.blue_iris_url
        self.username = settings.blue_iris_username
        self.password = settings.blue_iris_password
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with Blue Iris"""
        try:
            if not self.base_url or not self.username or not self.password:
                logger.warning("Blue Iris credentials not configured")
                return False
            
            auth_url = f"{self.base_url}/api/auth"
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    logger.info("Successfully authenticated with Blue Iris")
                    return True
                else:
                    logger.error(f"Blue Iris authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error authenticating with Blue Iris: {e}")
            return False
    
    async def get_cameras(self) -> List[Dict]:
        """Get list of cameras from Blue Iris"""
        try:
            if not await self.authenticate():
                return []
            
            cameras_url = f"{self.base_url}/api/cameras"
            async with self.session.get(cameras_url) as response:
                if response.status == 200:
                    cameras = await response.json()
                    logger.info(f"Retrieved {len(cameras)} cameras from Blue Iris")
                    return cameras
                else:
                    logger.error(f"Failed to get cameras: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting cameras: {e}")
            return []
    
    async def get_camera_status(self, camera_id: str) -> Dict:
        """Get status of a specific camera"""
        try:
            if not await self.authenticate():
                return {"error": "Authentication failed"}
            
            status_url = f"{self.base_url}/api/cameras/{camera_id}/status"
            async with self.session.get(status_url) as response:
                if response.status == 200:
                    status = await response.json()
                    return status
                else:
                    return {"error": f"Failed to get camera status: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting camera status: {e}")
            return {"error": str(e)}
    
    async def trigger_recording(self, camera_id: str, duration: int = 30) -> bool:
        """Trigger recording on a specific camera"""
        try:
            if not await self.authenticate():
                return False
            
            trigger_url = f"{self.base_url}/api/cameras/{camera_id}/trigger"
            trigger_data = {
                "duration": duration,
                "reason": "hummingbird_monitor"
            }
            
            async with self.session.post(trigger_url, json=trigger_data) as response:
                if response.status == 200:
                    logger.info(f"Triggered recording on camera {camera_id}")
                    return True
                else:
                    logger.error(f"Failed to trigger recording: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error triggering recording: {e}")
            return False
    
    async def get_motion_alerts(self, hours: int = 24) -> List[Dict]:
        """Get motion alerts from the last N hours"""
        try:
            if not await self.authenticate():
                return []
            
            alerts_url = f"{self.base_url}/api/motion/alerts"
            params = {"hours": hours}
            
            async with self.session.get(alerts_url, params=params) as response:
                if response.status == 200:
                    alerts = await response.json()
                    logger.info(f"Retrieved {len(alerts)} motion alerts")
                    return alerts
                else:
                    logger.error(f"Failed to get motion alerts: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting motion alerts: {e}")
            return []
    
    async def setup_webhook(self, webhook_url: str, events: List[str] = None) -> bool:
        """Setup webhook for Blue Iris events"""
        try:
            if not await self.authenticate():
                return False
            
            if events is None:
                events = ["motion", "recording_start", "recording_stop"]
            
            webhook_data = {
                "url": webhook_url,
                "events": events,
                "enabled": True
            }
            
            webhook_url_endpoint = f"{self.base_url}/api/webhooks"
            async with self.session.post(webhook_url_endpoint, json=webhook_data) as response:
                if response.status == 200:
                    logger.info(f"Webhook setup successful: {webhook_url}")
                    return True
                else:
                    logger.error(f"Failed to setup webhook: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting up webhook: {e}")
            return False
    
    async def get_system_status(self) -> Dict:
        """Get overall Blue Iris system status"""
        try:
            if not await self.authenticate():
                return {"error": "Authentication failed"}
            
            status_url = f"{self.base_url}/api/status"
            async with self.session.get(status_url) as response:
                if response.status == 200:
                    status = await response.json()
                    return status
                else:
                    return {"error": f"Failed to get system status: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def test_connection(self) -> Dict:
        """Test connection to Blue Iris"""
        try:
            test_url = f"{self.base_url}/api/ping"
            async with self.session.get(test_url, timeout=5) as response:
                if response.status == 200:
                    return {
                        "connected": True,
                        "response_time": response.headers.get("X-Response-Time", "unknown"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "connected": False,
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except asyncio.TimeoutError:
            return {
                "connected": False,
                "error": "Connection timeout",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
