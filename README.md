# projecttwo
To run this project, first install anaconda then follow steps <br/>
step 1 : **install dependencies**<br/>
open terminal and run follwing commands.
```
conda create --name myenv python=3.7.7
conda activate myenv
pip install django
python -m pip install -U channels
pip install scipy matplotlib imutils numpy opencv-python
conda install -c conda-forge dlib
```
step 2 :**run django server**<br/>
run this command in root directory where manage.py file is located.

```
python manage.py runserver

```
setp 3: **open website**<br/>
Go to your browser and follow this link [http://localhost:8000/chat](http://localhost:8000/chat)



