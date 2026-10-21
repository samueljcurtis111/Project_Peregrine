## October 20, 2026 — Dataset Factory Planning

**Goal:** Design and start the synthetic dataset generation system for Peregrine

**Plan:**
- Build separate generators for different model providers
- Create dynamically varied prompts for general knowledge and coding
- Store generated examples in JSONL format
- Add basic validation and duplicate detection for better dataset quality
- Track generation stats

**Research relevance:** The dataset factory will prepare instruction tuning data for Peregrine. The separate Polymorph research will investigate portable continued pretraining across TPU and GPU hardware 

**Changes & Decisions**

Change: Dropping external API providers
- **Original plan:** LLM's via google and groq api used for making dataset to train Peregrine
- **Problem / discovery:** Google doesn't allow their models to be used to train a competetive model and you need to be above 18 years old to use the api. Additionally, you also need to be 18 to use the groq api.
- **New decision:** Stick to just creating the dataset through a Self-hosted LLMs running on the kaggle 2x T4 gpu's.
- **Reason:** To avoid the identified API restrictions
- **Status:** Planned / Implementation started

Change: Swap from 2 llms running on Google Tpu's via kaggle to using the duel T4 GPU's via Kaggle. 
- **Original plan:** Run 2 large LLMs split across 4 of the TPU's each
- **Problem / discovery:** Overcomplicating the project when GPU's would work well and Kaggle provides more GPU hours.
- **New decision:** Swap from 2 llms running on Google Tpu's via kaggle to using the duel T4 GPU's via Kaggle.
- **Reason:** More GPU hours than TPU hours and simplification
- **Status:** Planned

**What I got Done**
- finish the prompt generator
- start the part that talks to the kaggle llm

**Next steps:**
- Parse the output
- Validate the response
- Save it to a JSONL file