from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    comment = models.TextField()
    status = models.BooleanField()
    last_view = models.DateTimeField('date published')

    def get_data(self):
        data = {"id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "comment": self.comment,
                "status": self.status}
        return data

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Face(models.Model):
    encoded = models.BinaryField()
    client = models.ForeignKey(Client, 
                            on_delete=models.CASCADE,
                            related_name="faces",
                            related_query_name="faces",)

