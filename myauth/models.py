from django.db import models
import json
import base64
from django.contrib.auth.models import AbstractUser
# Create your models here.

class UserProfile(AbstractUser):
    _prefs = models.TextField(db_column='_prefs', blank=True)

    def decode_prefs(self):
        try:
            #ret = json.loads(base64.decodestring(self._prefs))
            ret = json.loads(self._prefs)
        except: 
            ret = dict()
        return ret

    def save_prefs(self, prefs):
        #self._prefs = base64.encodestring(json.dumps(prefs))
        self._prefs = json.dumps(prefs)
        self.save()

    def get_pref(self, key):
        prefs = self.decode_prefs()
        if key in prefs.keys():
            return prefs[key]
        else:
            return None

    def set_pref(self, key, val):
        prefs = self.decode_prefs()
        prefs[key] = val
        self.save_prefs(prefs) 



