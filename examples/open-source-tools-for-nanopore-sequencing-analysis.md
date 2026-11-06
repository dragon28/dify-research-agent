# Open-source tools for nanopore sequencing analysis

## Summary
Nanopore sequencing is a technology that allows for the direct reading of DNA sequences through a nanopore. This method, while offering long-read capabilities, faces challenges such as low resolution and high error rates due to the rapid movement of DNA through the nanopore. Despite these challenges, several open-source tools have been developed to aid in the analysis of nanopore sequencing data, including basecalling, error correction, and identification of modified nucleotides.

## Findings
### Basecalling Tools
- **Nanocall** ([4, 7, 8]): A C++-based open-source basecaller for Oxford Nanopore sequencing data.
- **Dorado** ([7, 9]): A production basecaller from 2022, which is the successor to Guppy.
- **Bonito** ([4]): A PyTorch basecaller for Oxford Nanopore reads, currently in research phase.

### Data Analysis Tools
- **Pod5** ([5]): A high-performance file format for nanopore reads.
- **Mahi-mahi** ([5]): A command-line bioinformatics tool for analyzing tandem repeat loci from long-read nanopore sequencing data.
- **Megalodon** ([9]): A tool that takes raw nanopore reads as input and produces various outputs, including basecalls, reference mappings, sequence variant calls, and modified base calls.
- **Tombo** ([9]): A suite of tools for identifying modified nucleotides from nanopore sequencing data.

### Error Correction and Analysis
- **NanoOK** ([10]): An open-source software proposed by Legget et al. to compare sets of references versus reads, aiming to delimit the landscape of errors made by MinION and other Nanopore sequencers.

## Open questions
- The rapid changes in equipment, chemistry, and programs pose challenges for the development and maintenance of open-source tools, as highlighted by the limited number of papers addressing error correction methods.
- The lack of publicly available benchmarks and software content from Oxford Nanopore Technologies (ONT) complicates the task of accurately assessing and improving the performance of nanopore sequencing tools.
- The initial sequencing pores are often limited, which can affect the quality and quantity of data obtained, as noted in the Reddit post from January 2025.
- The high intrinsic error rate of nanopore sequencing remains a significant challenge, as highlighted by the need for robust error correction methods and tools.

## References

4. [GitHub - GoekeLab/awesome-nanopore: A curated list of awesome ...](https://github.com/goekelab/awesome-nanopore)
5. [Oxford Nanopore Technologies · GitHub](https://github.com/nanoporetech)
7. [GitHub - GoekeLab/awesome-nanopore: A curated list of awesome ...](https://github.com/GoekeLab/awesome-nanopore)
8. [Nanocall: an open source basecaller for Oxford Nanopore ... - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5408768/)
9. [GitHub - seanaller/nanoporeBioinformatics: Collection of ...](https://github.com/seanaller/nanoporeBioinformatics)
10. [Sequencing DNA with nanopores: Troubles and biases - PMC - NIH](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486125/)
