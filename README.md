# django-db-introspection
Django 数据库内省工具, 通过数据表名就可以动态创建一个即时可用的Django models对象。
仅仅需要一个表名，你就可以立即得到一个可用的Django 模型，并立即进行查询，更新等操作，开箱即用。
目前版本暂时不支持外键关联关系。
# -------------------------------
Django database introspection tool, through the data table name can dynamically create a Django models ready-to-use objects.
Just need a table name, you can immediately get a usable Django model, and immediately query, update and other operations, out of the box.
The current version does not support foreign key relationships.
# -------------------------------
```
In [4]: from monkey_king.testdj import get_my_models

In [5]: client_device_user = get_my_models('monkey_king', 'client_device_user')
class ClientDeviceUser(models.Model):
    box_id = models.CharField(max_length=20)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=37)
    name4user = models.CharField(max_length=50, blank=True, null=True)
    email = models.IntegerField(blank=True, null=True)
    sms = models.IntegerField(blank=True, null=True)
    voice = models.IntegerField(blank=True, null=True)
    push = models.IntegerField(blank=True, null=True)
    master = models.IntegerField(blank=True, null=True)
    agent = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table='client_device_user'
/usr/local/lib/python3.5/dist-packages/django/db/models/base.py:325: RuntimeWarning: Model 'monkey_king.clientdeviceuser' wasalready registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.
  new_class._meta.apps.register_model(new_class._meta.app_label, new_class)
0.019804232000751654

In [6]: client_device_user.objects.first().box_id
Out[6]: '01J01ELQ15'

In [7]:
```
