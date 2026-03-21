# Auto-generated shim to add missing SFMAdapter methods to avoid AttributeError -> fallback
import logging
try:
    from app.security import sfm_adapter as _sfm_adapter
    SFMAdapter = getattr(_sfm_adapter, 'SFMAdapter', None)
except Exception:
    SFMAdapter = None

if SFMAdapter is not None:
    def _make_stub(name):
        def _stub(self, *args, **kwargs):
            logging.getLogger('sfm_shim').warning('Called shim for missing SFMAdapter.%s', name)
            return {
                'success': False,
                'result': 'mock_fallback',
                'source': 'sfm_mock',
                'message': f'shimbed:{name}'
            }
        return _stub

    # Methods detected from logs
    methods = [
        'get_parental_control_settings',
        'get_time_limits',
        'get_schedules',
        'get_geofences',
        'get_app_blocks',
        'delete_location_geofence',
        'delete_geofence',
        'get_subscription_status'
    ]
    
    for m in methods:
        if not hasattr(SFMAdapter, m):
            setattr(SFMAdapter, m, _make_stub(m))
