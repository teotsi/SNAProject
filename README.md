# SNAProject
Project for Social Networks Analysis course @DMST, AUEB.
Using web scraping techniques to create a dataset of a network, using chords as nodes and chord transitions as edges.

Final report is available in `report.pdf` for now, until the Markdown version is completed.
Dataset scraped from https://kithara.to/. For (practically) unlimited access to songs, a `cookie.txt` file must be present in the same folder as the python script, containing the session cookie of the user(access is restricted for guests). Creating accounts is easy and free.

After collecting all the data, candidate(potential) chords are (when necessary) translated from flat to sharp, separated (there's no specific standard enforced by kithara.to, so there's a significant amount of users that upload songs whose chords need to be tokenized), and finally output in an `edges.csv` and a `nodes.csv` file, which can then be imported into software such as Gephi.

>Άνετα μιλάω τώρα και σε μπακαλιάρους, σε κατσαβίδια και σε λογισμικά.
