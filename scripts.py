from ClassRoom.models import Assignment,Classes

print(Classes.objects.get(id=2))
print(Assignment.objects.get(id=1,for_class__id=2))