# Open-source tools for nanopore sequencing analysis

## Summary
Nanopore sequencing is a promising technology for long-read sequencing, but it faces challenges such as high error rates and rapid DNA strand movement through the nanopore. This report highlights open-source tools that can be used for nanopore sequencing analysis, focusing on basecalling, error correction, and data processing.

## Findings
### Basecalling Tools
- **Dorado** [4, 7]: A state-of-the-art basecalling software for Oxford Nanopore Technology (ONT) platforms, supporting both fast5 and pod5 formats.
- **Nanocall** [7]: An open-source basecaller for Oxford Nanopore sequencing data, written in C++.
- **EPI2ME** and **What's In My Pot**: Open-source tools that offer flexibility but require significant computational expertise [5].

### Mapping and Signal Processing Tools
- **Sigmap**: A nanopore raw signal mapper tool for real-time selective sequencing [6].
- **UNCALLED**: An open-source mapper that rapidly matches streaming nanopore current signals [6].

### Data Analysis Tools
- **Megalodon**: Takes raw nanopore reads as input and produces basecalls, reference mappings, sequence variant calls, and modified base calls [9].
- **Tombo**: A suite of tools for identifying modified nucleotides from nanopore sequencing data [9].

### Bioinformatics Challenges
- Nanopore sequencing faces distinct implementation hurdles, particularly in bioinformatics, where open-source tools like EPI2ME and What's In My Pot offer flexibility but require significant computational expertise [5].

### Error Correction and Signal Decoding
- **BaseNet**: A transformer-based toolkit for nanopore sequencing signal decoding, providing state-of-the-art algorithms [8].

## Open questions
- How can open-source tools be further improved to address the bioinformatics challenges associated with nanopore sequencing?
- What are the best practices for integrating open-source tools into clinical workflows to ensure accuracy and ease of use?
- How can the high error rates in nanopore sequencing be effectively mitigated using these tools and others?

## References

4. [Unlocking the full potential of nanopore sequencing: tips, tricks, ...](https://academic.oup.com/nar/article/54/3/gkag023/8454528)
5. [Current status and prospects of nanopore sequencing technology in ...](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2026.1843102/full)
6. [Portable nanopore-sequencing technology: Trends in development ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC9929578/)
7. [GitHub - GoekeLab/awesome-nanopore: A curated list of awesome ...](https://github.com/GoekeLab/awesome-nanopore)
8. [A transformer-based toolkit for nanopore sequencing signal decoding](https://www.sciencedirect.com/science/article/pii/S2001037024003040)
9. [GitHub - seanaller/nanoporeBioinformatics: Collection of ...](https://github.com/seanaller/nanoporeBioinformatics)
