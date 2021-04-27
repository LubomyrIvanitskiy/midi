# midi
Python pretty_midi wrapper

!pip install -r requirements.txt

The following code snippet will read a demo midi file and save each track separatelly

```python
from  midiwrap import MidiFile, dataframe_to_midi


midi = MidiFile('data/fur_elise.mid')
track_names = midi.track_names()
print("Tracks: ", track_names)
for track_name in track_names:
    dataframe_to_midi(midi.notes[midi.notes.Name == track_name], f"data/out_fur_elise_{track_name.lower()}.mid")
midi.to_csv("out_to_elise.csv")
```

To list all notes, call `midi.notes`

midi.notes is a pandas dataframe, so you can modify midi.notes however you want with pandas tools and then call `dataframe_to_midi()` to save the result

An example of `midi.notes` dataframe:
![image](https://user-images.githubusercontent.com/30999506/116210545-a48caa80-a74b-11eb-8dcc-e81f9ac2a640.png)

