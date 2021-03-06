# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib, urllib.request, ssl, re

from django.db import models
from django.contrib import messages
from apps.login_registration.models import User

URL_REGEX = re.compile(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

class ClothingManager(models.Manager):
    def basic_validator(self, newrequest):
        bFlashMessage = False

        name = newrequest.POST['textName']
        imageURL = newrequest.POST['textImageURL']

        # Name - Required; Can't be blank
        if len(name) < 1:
            messages.error(newrequest, u"[Name cannot be blank]", extra_tags="name")
            bFlashMessage = True  

        # Image URL - Required; Can't be blank
        if len(imageURL) < 1:
            messages.error(newrequest, u"[Image URL cannot be blank]", extra_tags="imageurl")
            bFlashMessage = True  

        # Image URL should be re-used by the user so we'll error out if they try to reuse the same URL
        # Logically it shouldn't appear in either tops or bottoms
        objTopImage = Top.objects.filter(imageURL=imageURL)
        objBottomImage = Bottom.objects.filter(imageURL=imageURL)        
        if objTopImage.count() > 0 or objBottomImage.count() > 0:
            messages.error(newrequest, u"[Image URL already in database!]", extra_tags="imageurl")
            bFlashMessage = True 

        # Image URL must be publically visible and have a content type of image
        if not URL_REGEX.match(imageURL):
            messages.error(newrequest, u"[Invalid Image URL!]", extra_tags="imageurl")
            bFlashMessage = True 
        else:   
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                r = urllib.request.urlopen(imageURL)
                if (r.headers.get_content_maintype() != 'image'):
                    messages.error(newrequest, u"[Image URL must be public and valid and resolve to content type of image]", extra_tags="imageurl")
                    bFlashMessage = True
            except urllib.error.URLError as e:
                messages.error(newrequest, u"[An error occurred when checking the URL]", extra_tags="imageurl")
                bFlashMessage = True
            except urllib.error.HTTPError as e:
                messages.error(newrequest, u"[An error occurred when checking the URL]", extra_tags="imageurl")
                bFlashMessage = True                

        return bFlashMessage
    
    def db_check(request, postData):
        bFlashMessage = False
        check = Top.objects.filter(imageURL = postData.POST['textImageURL'])
        if len(check):
            messages.error(postData, u"[You have already uploaded this image]", extra_tags="imageurl")
            bFlashMessage = True

        return bFlashMessage


class ComboManager(models.Manager):
    def combo_validator(self, comboData):

        bFlashMessage = False

        tops = Combo.objects.filter(top_chosen_id=comboData.POST['currentTopID'])
        tops_bottoms = tops.filter(bottom_chosen_id=comboData.POST['currentBottomID'])
        if tops_bottoms.count() > 0:
            messages.error(comboData, u"[This Combo already exists]", extra_tags="combo")
            bFlashMessage = True

        return bFlashMessage




class Top(models.Model):
    name = models.CharField(max_length=255)
    imageURL = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    #relationships
    top_added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="combo_top_added_by")
    objects = ClothingManager()

class Bottom(models.Model):
    name = models.CharField(max_length=255)
    imageURL = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    # relationships
    bottom_added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="combo_bottom_added_by")
    objects = ClothingManager()   

class Combo(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    # relationships
    top_chosen = models.ForeignKey(Top, null=True, on_delete=models.SET_NULL, related_name="combo_top")
    bottom_chosen = models.ForeignKey(Bottom, null=True, on_delete=models.SET_NULL, related_name="combo_bottom")    
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="combo_by")  
    objects = ComboManager()

class Schedule(models.Model):
    date_scheduled = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    # relationships
    combo_chosen = models.ForeignKey(Combo, null=True, on_delete=models.SET_NULL, related_name="chosen_combo")
    scheduled_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="combo_scheduled_by")    