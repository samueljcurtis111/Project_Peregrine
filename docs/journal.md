## October 20, 2026 — Dataset Factory Planning

**Goal:** Design and start the synthetic dataset generation system for Peregrine

**Plan:**
- Build separate generators for different model providers
- Create dynamically varied prompts for general knowledge and coding
- Store generated examples in JSONL format
- Add basic validation and duplicate detection for better dataset quality
- Track generation stats

**Research relevance:** The dataset factory will prepare instruction tuning data for Peregrine. The separate Polymorph research will investigate portable continued pretraining across TPU and GPU hardware 

### Changes & Decisions

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

### What I got Done
- finish the prompt generator
- start the part that talks to the kaggle llm

### Next steps:
- Parse the output
- Validate the response
- Save it to a JSONL file



## October 21, 2026 — Dataset Factory Progress

**Goal:** Get the dataset generator working and build the scripts to clean and validate the generated data.

**Plan:**
- Finish the script that communicates with the self-hosted LLM
- Parse and save the generated question/answer pairs
- Make a separate script to remove duplicate questions
- Add dataset validation and track how many examples pass or fail
- Get everything ready for testing with the Kaggle GPUs

**Research relevance:** The dataset factory will generate synthetic instruction tuning data for Peregrine. This is separate from the actual pretraining dataset and the Polymorph research.

### Changes & Decisions

**Change: Keeping dataset cleaning in separate scripts**
- **Original plan:** Have the generator handle most of the dataset processing
- **New decision:** Make separate scripts for generating, removing duplicates, and validating examples
- **Reason:** Keeps everything more organized and makes it easier to fix stuff without messing with the rest of the code
- **Status:** Implemented

**Change: Generate first, clean afterward**
- **Original plan:** Check for duplicates while generating examples
- **New decision:** Save the generated examples first, then run a separate script to remove duplicates
- **Reason:** Simpler to implement for now, and I can keep the original dataset in case I need it later
- **Status:** Implemented

### What I Got Done
- Finished the basic script that sends prompts to the LLM and parses the JSON response
- Added checks to make sure the generated questions and answers aren't empty
- Made it save examples to a JSONL file
- Added a generation loop with success and attempt counters
- Added error handling so one failed response doesn't stop everything
- Made `duplicates.py` to remove repeated questions and save the unique ones to a new file
- Added counters to track total examples, duplicates, and unique examples
- Started `validate.py` to check the dataset for invalid JSON and missing questions or answers
- Added counters for valid and invalid examples
- Did a lot more Python coding myself instead of just having AI write everything

### Next Steps
- Finish the validation script and add a summary of the results
- Make the validator save valid examples to `output_clean.jsonl`
- Test the entire pipeline with a small dataset
- Fix any issues that show up during testing
- Start generating larger datasets once everything is working reliably

**Overall:** Made pretty good progress today. Most of the basic dataset factory code is written now. Still need to actually test everything together, but the generation, duplicate removal, and validation parts are mostly done.