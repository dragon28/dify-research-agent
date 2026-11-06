# Open-source tools for nanopore sequencing analysis

## Summary
Nanopore sequencing is a powerful technology that allows for real-time direct sequencing of DNA and RNA. This technology has seen significant advancements, with the first nanopore sequencing instrument developed by Oxford Nanopore Technologies (ONT) in the 2010s. The technology works by measuring ionic current fluctuations as single DNA or RNA molecules translocate through nano-scale pores. Despite its potential, nanopore sequencing faces challenges such as high error rates and the need for robust data analysis tools.

## Findings
### Basecalling Tools
- **BaseNet**: An open-source toolkit for nanopore sequencing signal decoding based on state-of-the-art transformer algorithms [7].
- **Dorado**: A production basecaller from 2022, which is the successor to Guppy [8].
- **Nanocall**: An open-source basecaller for Oxford Nanopore sequencing data [8].

### Data Analysis Tools
- **Megalodon**: A toolkit that produces basecalls, reference mappings, sequence variant calls, and modified base calls [9].
- **Tombo**: A suite of tools for the identification of modified nucleotides from nanopore sequencing data [9].

### Challenges and Analysis
- **NanoOK**: An open-source software proposed by Legget et al. to compare sets of references versus reads, helping to analyze sequencing errors [10].
- **Oxford Nanopore Technology**: Provides tools for direct, real-time sequencing and detection of modified bases, requiring a designated basecalling model [11].

## Open questions
- How can the high error rate of raw sequencing data be effectively managed and corrected?
- What are the best practices for removing host background nucleic acids in complex samples?
- How can the cost-benefit ratio of nanopore sequencing be further optimized?
- What are the specific failure modes encountered when there is no-to-low input DNA into a sequencing device, and how can they be mitigated?

## References

7. [BaseNet: A transformer-based toolkit for nanopore sequencing ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC11465205/)
8. [GitHub - GoekeLab/awesome-nanopore: A curated list of awesome ...](https://github.com/GoekeLab/awesome-nanopore)
9. [GitHub - seanaller/nanoporeBioinformatics: Collection of ...](https://github.com/seanaller/nanoporeBioinformatics)
10. [Sequencing DNA with nanopores: Troubles and biases - PMC - NIH](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486125/)
11. [Data analysis - Oxford Nanopore Technologies](https://nanoporetech.com/document/data-analysis)
