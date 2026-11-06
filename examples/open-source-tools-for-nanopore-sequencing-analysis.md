# Open-source Tools for Nanopore Sequencing Analysis

## Summary
Nanopore sequencing is a powerful technique for direct DNA base detection, offering high portability and the ability to detect DNA modifications. However, the rapid movement of DNA through the nanopore and the associated background noise make data processing challenging. Several open-source tools are available for basecalling and analysis, including Nanocall and Openfish, which provide alternatives to proprietary software.

## Findings
### Basecalling Tools
- **Nanocall** [n4, n7, n8]: An open-source basecaller for Oxford Nanopore sequencing data, written in C++.
- **Bonito** [n4]: A PyTorch-based basecaller for Oxford Nanopore reads, also in research phase.
- **Openfish** [n6]: An open-source GPU-accelerated nanopore basecaller decoding library.
- **Slorado** [n6]: A fully open-source basecalling framework that supports both DNA and RNA with equivalent accuracy to Dorado.

### Data Analysis Tools
- **Megalodon** [n9]: Takes raw nanopore reads as input and produces various outputs, including basecalls, reference mappings, and sequence variant calls.
- **Tombo** [n9]: A suite of tools for identifying modified nucleotides from nanopore sequencing data.

### Challenges and Landscape
- The rapid changes in equipment, chemistry, and software make it difficult to fully characterize errors in nanopore sequencing [n10, n12].
- **NanoOK** [n10]: An open-source software for comparing sets of references versus reads, which helps in error correction.

### Performance and Comparison
- Numerous tools have been developed to leverage the direct detection of DNA base modifications by Oxford Nanopore sequencing [n5].
- Open-source tools like Openfish and Slorado remove the hardware lock-in that currently limits high-performance nanopore basecalling [n6].

## Open questions
- How do the performance and accuracy of open-source tools like Nanocall and Bonito compare to proprietary tools such as Guppy?
- What are the specific challenges in characterizing errors in nanopore sequencing, and how can open-source tools like NanoOK address these challenges?
- How can the rapid changes in nanopore technology be managed to ensure consistent and reliable data analysis?

## References

_No sources cited._
