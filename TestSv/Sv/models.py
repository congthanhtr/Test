# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Baseconfigtable(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=500, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BaseConfigTable'


class ConfigimpactTour(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=500, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    tourproperty = models.CharField(db_column='TourProperty', max_length=500, blank=True, null=True)  # Field name made lowercase.
    tourimpact = models.BooleanField(db_column='TourImpact', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigImpact_Tour'


class ConfigweightService(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=500, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    serviceproperty = models.CharField(db_column='ServiceProperty', max_length=500, blank=True, null=True)  # Field name made lowercase.
    serviceweight = models.IntegerField(db_column='ServiceWeight', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigWeight_Service'


class ConfigweightTour(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    log_createdate = models.DateField(db_column='Log_CreateDate', blank=True, null=True)  # Field name made lowercase.
    log_createby = models.BigIntegerField(db_column='Log_CreateBy', blank=True, null=True)  # Field name made lowercase.
    log_updatedate = models.DateField(db_column='Log_UpdateDate', blank=True, null=True)  # Field name made lowercase.
    log_updateby = models.BigIntegerField(db_column='Log_UpdateBy', blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=500, blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted')  # Field name made lowercase.
    tourproperty = models.CharField(db_column='TourProperty', max_length=500, blank=True, null=True)  # Field name made lowercase.
    weight = models.IntegerField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ConfigWeight_Tour'