FROM mongo:4.4

COPY songs.json /songs.json
CMD mongoimport --host mongodb --db songsdb --collection songs --drop --type json --file /songs.json