# How to run

```bash
pip install -r requirements.txt
```

```bash
cd TestSv
```

```python
python manage.py runserver
```

# Implement ML model

TestSv -> Sv -> ml_model

model and its implementation should be in the same folder

# How to use post api of predict_places and predict_vehicles

1. predict_places: pass an json like --> return value is places should go in one province
{
  "data": [2,3,4.1] // [0] day(s) spending in one province, [1] travel time to one province, [2] money that individual had to pay (vnd milion)
}

2. predict_vehicle: pass json like --> return value is boolean value that decide should we go by plane or not:
{
  "data": [1680,60,1790,3,3,0] 
  // [0] disatnce(km) from A to B, [1] plane travel time, [2] bus travel time, [3] days, [4] // nights, [5] 0 is cheap and 1 is expensive tour
}

