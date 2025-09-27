from typing import Dict, Optional, Callable
import asyncio
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.progress_data: Dict[str, Dict] = {}
        self.websocket_connections: Dict[str, list] = {}

    def create_session(self, session_id: str, total_items: int):
        """Create a new progress tracking session"""
        self.progress_data[session_id] = {
            'total': total_items,
            'current': 0,
            'stage': 'initializing',
            'message': 'Starting processing...',
            'start_time': datetime.now().isoformat(),
            'errors': [],
            'completed': False,
            'api_progress': {
                'storeleads': {'current': 0, 'total': total_items},
                'companyenrich': {'current': 0, 'total': 0},
                'scoring': {'current': 0, 'total': total_items}
            }
        }

    def update_progress(self, session_id: str, current: int = None, stage: str = None,
                       message: str = None, error: str = None, api_progress: Dict = None):
        """Update progress for a session"""
        if session_id not in self.progress_data:
            return

        session = self.progress_data[session_id]

        if current is not None:
            session['current'] = current

        if stage:
            session['stage'] = stage

        if message:
            session['message'] = message

        if error:
            session['errors'].append({
                'time': datetime.now().isoformat(),
                'error': error
            })

        if api_progress:
            session['api_progress'] = api_progress

        # Calculate overall percentage based on all API progress
        if 'api_progress' in session:
            api_data = session['api_progress']
            # Calculate weighted progress
            storeleads_weight = 0.4
            companyenrich_weight = 0.3 if api_data['companyenrich']['total'] > 0 else 0
            scoring_weight = 0.3

            # Adjust weights if no Company Enrich
            if companyenrich_weight == 0:
                storeleads_weight = 0.5
                scoring_weight = 0.5

            storeleads_pct = (api_data['storeleads']['current'] / max(api_data['storeleads']['total'], 1)) * 100
            companyenrich_pct = (api_data['companyenrich']['current'] / max(api_data['companyenrich']['total'], 1)) * 100 if api_data['companyenrich']['total'] > 0 else 0
            scoring_pct = (api_data['scoring']['current'] / max(api_data['scoring']['total'], 1)) * 100

            session['percentage'] = round(
                storeleads_pct * storeleads_weight +
                companyenrich_pct * companyenrich_weight +
                scoring_pct * scoring_weight, 1
            )
        elif session['total'] > 0:
            session['percentage'] = round((session['current'] / session['total']) * 100, 1)
        else:
            session['percentage'] = 0

        # Calculate elapsed time
        start_time = datetime.fromisoformat(session['start_time'])
        elapsed = (datetime.now() - start_time).total_seconds()
        session['elapsed_time'] = round(elapsed, 1)

        # Estimate remaining time
        if session['current'] > 0 and session['current'] < session['total']:
            rate = session['current'] / elapsed
            remaining_items = session['total'] - session['current']
            session['estimated_remaining'] = round(remaining_items / rate, 1)
        else:
            session['estimated_remaining'] = 0

    def complete_session(self, session_id: str, success: bool = True, message: str = None):
        """Mark a session as complete"""
        if session_id not in self.progress_data:
            return

        session = self.progress_data[session_id]
        session['completed'] = True
        session['success'] = success
        session['current'] = session['total']
        session['percentage'] = 100 if success else session.get('percentage', 0)

        if message:
            session['message'] = message
        elif success:
            session['message'] = 'Processing completed successfully!'
        else:
            session['message'] = 'Processing failed. Check errors for details.'

    def get_progress(self, session_id: str) -> Optional[Dict]:
        """Get current progress for a session"""
        return self.progress_data.get(session_id)

    def cleanup_session(self, session_id: str):
        """Remove session data after completion"""
        if session_id in self.progress_data:
            del self.progress_data[session_id]
        if session_id in self.websocket_connections:
            del self.websocket_connections[session_id]

# Global progress tracker instance
progress_tracker = ProgressTracker()