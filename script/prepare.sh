echo 'db="""' > ./endpoint/main.py
cat ./data/*.csv >> ./endpoint/main.py
echo '"""' >> ./endpoint/main.py
cat ./endpoint/main.t.py >> ./endpoint/main.py