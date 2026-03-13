# dead-reckoning

**A living apprenticeship. The master's knowledge, preserved forever.**

---

## The Problem

Every skilled trade carries knowledge that lives only in people - in their hands, their judgment, the accumulated pattern of ten thousand decisions made at the bench. When those people die, that knowledge dies with them.

Harold Jennings is 81. He's been repairing mechanical clocks and watches in Lancaster, Pennsylvania since 1967. He learned from Raymond Kessler, who learned from a German-trained clockmaker in Philadelphia, who learned from someone before him. That lineage goes back centuries.

Harold knows things that are not in any book. He knows what a correctly running gear train *feels* like. He knows the sound an escapement makes when it is about to fail. He knows how much pressure to apply to a pivot that won't come free, and why applying more pressure is always the wrong answer. He knows this because he has been wrong, and watched others be wrong, and corrected himself and them - for nearly sixty years.

There are fewer and fewer people like Harold. And when they go, they take the knowledge with them.

dead-reckoning is an attempt to change that.

---

## What It Does

dead-reckoning is a RAG-powered AI mentor built on DigitalOcean's Gradient AI platform. It preserves Harold Jennings' knowledge - his technical writing, his interview transcripts, his case studies - in a knowledge base, and makes it available through a conversational interface where Harold answers as himself.

You don't ask a chatbot. You ask Harold.

He will tell you why a deadbeat escapement is less forgiving than a recoil anchor. He will walk you through diagnosing an intermittent fault in a Dutch Staartklok. He will tell you about the 1891 Vienna Regulator and what the bent pendulum rod was doing to the escapement geometry. He will tell you that the clock doesn't know you meant well.

You can also show him a photograph. Upload an image of a movement, a damaged wheel, a worn escapement - and Harold will tell you what he sees.

---

## Demo

> Ask Harold anything about clockmaking.

```
You: What's the difference between a recoil anchor and a deadbeat escapement?

Harold: Sit down. This matters and I want to explain it properly.

The anchor escapement — the one you'll find in most grandfather clocks made after
1700 — has a flaw built into its design. At the moment of unlocking, the escape
wheel reverses direction slightly before continuing forward. Recoil. You can see it
in the second hand of any clock with one: a tiny backward stutter on every tick.
That's not a defect. That's the escapement doing what it was designed to do.

The deadbeat was George Graham's answer to that problem, around 1715. He shaped
the locking faces of the pallets on a radius centered on the pallet arbor. When a
tooth rests on that face, it exerts no net force — neither forward nor backward.
The wheel stops. Dead. No recoil.

The consequence for accuracy is significant. In a recoil escapement, the gear train
is involved in every swing of the pendulum — the reversal means friction and inertia
are disturbing the pendulum constantly. In a deadbeat, the gear train truly stops
during the locking phase. The pendulum is left alone. It swings more consistently.

Why doesn't every clock use a deadbeat? Because it's unforgiving. The locking face
geometry has to be exact. Get it slightly wrong and you get partial recoil — which
is worse than proper recoil, because it's inconsistent. I've seen repair jobs where
someone polished the pallet faces and accidentally made the clock less accurate.

Rule for deadbeat work: if you're not certain you can restore the correct geometry,
clean and lubricate only. Don't reshape unless you have a clear defect to correct
and a clear plan for correcting it.
```

---

## Gradient AI Features Used

| Feature | How dead-reckoning uses it |
|---|---|
| **Knowledge Bases** | Harold's entire corpus - 12 documents, ~18,000 words of technical notes, interview transcripts, and case studies - is indexed in a Gradient AI Knowledge Base with the GTE Large EN embedding model, giving the agent grounded, retrievable access to his specific knowledge and memories. |
| **Serverless Inference** | All Harold responses are generated via the Gradient AI serverless inference endpoint, with no model infrastructure to manage. |
| **Agent Development Kit** | Harold is deployed as a Gradient AI Agent (harold-jennings-v2, running Llama 3.3 Instruct 70B) with his persona and system prompt configured at the platform level, connecting the knowledge base to the inference model in a single agent endpoint. |
| **Function Calling** | The `/query/image` endpoint uses the Anthropic Vision API to extract a technical description from a clock photograph, then passes that description to Harold as a structured prompt - a form of chained tool use between the vision model and the Harold agent. |
| **Agent Evaluations** | A 15-case evaluation suite tests Harold's responses against key phrases drawn from the source corpus, verifying that the knowledge base retrieval is working and that Harold's answers are grounded in his actual documented knowledge. |

---

## Architecture

```
                        ┌─────────────────┐
                        │  frontend       │
                        │  index.html     │
                        │  (vanilla JS)   │
                        └────────┬────────┘
                                 │ HTTP / SSE
                        ┌────────▼────────┐
                        │  FastAPI        │
                        │  backend        │
                        │  main.py        │
                        └──┬──────────┬───┘
                           │          │
              ┌────────────▼──┐   ┌───▼──────────────────┐
              │ persona/      │   │ vision/               │
              │ agent.py      │   │ image_handler.py      │
              │               │   │                       │
              │ ask_harold()  │   │ analyze_clock_image() │
              │ ask_harold_   │   │                       │
              │ stream()      │   │ -> Anthropic Vision   │
              └──────┬────────┘   │   API (description)   │
                     │            │ -> ask_harold()        │
                     │            └───────────────────────┘
                     │
         ┌───────────▼──────────────────────────┐
         │  DigitalOcean Gradient AI             │
         │                                      │
         │  Agent: harold-jennings-v2            │
         │         (Llama 3.3 70B)              │
         │  ┌──────────────────┐                │
         │  │ Knowledge Base   │                │
         │  │ 12 documents     │                │
         │  │ GTE Large EN     │                │
         │  └──────────────────┘                │
         │  Serverless Inference                │
         └──────────────────────────────────────┘
```

**Components:**

- **FastAPI backend** - three endpoints: `POST /query` (full response), `POST /query/stream` (SSE streaming), `POST /query/image` (vision + Harold)
- **Harold persona prompt** - a 500-word character brief in `backend/persona/harold.py` defining voice, memory, constraints, and knowledge domain; configured as the agent's system instruction
- **18,000-word corpus** - 12 source documents across technical notes, interview transcripts, and repair case studies, indexed in a Gradient AI Knowledge Base
- **Streaming SSE** - `ask_harold_stream()` streams the agent's response token by token via `httpx.AsyncClient.stream()`, yielding `data:` events consumed by the frontend's `ReadableStream` reader
- **Vision pipeline** - clock photographs are described by Claude's vision capability, then that technical description is passed to Harold as a first-person observation prompt

---

## Running Locally

```bash
git clone https://github.com/your-username/dead-reckoning
cd dead-reckoning
pip install fastapi uvicorn httpx python-dotenv anthropic
```

Copy `.env.example` to `.env` and fill in your keys:

```
DIGITALOCEAN_API_KEY=...
GRADIENT_AI_AGENT_ID=...
KNOWLEDGE_BASE_UUID=...
ANTHROPIC_API_KEY=...
AGENT_ENDPOINT=...
AGENT_ACCESS_KEY=...
```

Start the backend:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `frontend/index.html` in a browser.

**To build the knowledge base from scratch:**

```bash
# Create the knowledge base
python backend/ingestion/create_knowledge_base.py

# Upload the corpus
python backend/ingestion/upload_files.py

# Trigger indexing
python backend/ingestion/trigger_indexing.py

# Create the Harold agent
python backend/ingestion/create_agent.py
```

**To run evaluations:**

```bash
python backend/ingestion/run_evaluations.py
```

---

## The Corpus

Harold Jennings is a fictional character, but his knowledge is real - drawn from the technical literature of mechanical horology, including the repair traditions documented by Britten, Rawlings, and the NAWCC.

The corpus comprises 12 documents in three categories:

**Technical notes** - Harold's written reference material for apprentices:
- `escapements_verge_and_anchor.md` - verge and anchor escapement mechanics, failure modes, adjustment, lubrication
- `mainspring_diagnosis.md` - failure modes, sizing, barrel inspection, when to replace
- `cleaning_solutions_harold_method.md` - full cleaning procedure, solutions, special cases
- `common_mistakes_beginners_make.md` - seven documented mistakes with causes, consequences, and lessons

**Interview transcripts** - conversations with Harold recorded by his apprentice Sarah Okafor:
- `interview_1967_apprenticeship.md` - Raymond Kessler, the early years, learning to feel a gear train
- `interview_1974_first_shop.md` - opening the Lancaster shop, first customers, early mistakes
- `interview_1989_difficult_repair.md` - the Dutch Staartklok case; teaching philosophy
- `interview_2003_teaching.md` - what makes a good apprentice; the future of the craft
- `interview_2019_the_craft_dying.md` - late reflections; what Harold hopes survives

**Case studies** - detailed repair narratives written by Harold from bench notes:
- `the_1891_vienna_regulator.md` - deadbeat pallet irregularity, bent pendulum rod, diagnosis through observation
- `the_dutch_staartklok_mystery.md` - three weeks, a temperature-dependent crutch pin failure, a question from Vermont
- `the_apprentice_who_broke_a_fusee.md` - a broken fusee chain, an assumption, and the rule about unexpected resistance

---

## Evaluation

The evaluation suite in `backend/ingestion/run_evaluations.py` tests 15 cases drawn from the corpus, covering:

- Escapement mechanics and lubrication
- Mainspring failure modes and replacement criteria
- Cleaning procedure and philosophy
- Common beginner mistakes
- Harold's apprenticeship under Raymond Kessler
- Specific repair cases (Vienna Regulator, Dutch Staartklok)
- Teaching philosophy

Each case checks whether key phrases from the expected answer - phrases drawn directly from Harold's source documents - appear in the actual response. A case passes if at least three key phrases match. This tests not just that Harold answers plausibly, but that the knowledge base retrieval is returning the right documents and that Harold's answers are grounded in his specific documented knowledge rather than generic horological information.

Results are saved to `data/evaluations/eval_results.json`.

---

## License

MIT

---

*dead-reckoning was built for the DigitalOcean Gradient AI Hackathon, 2026.*

*The name comes from the navigational technique of estimating one's current position using a known past position, speed, and direction - without external reference. A clockmaker reading a movement does something similar: working forward from what the parts reveal, estimating what happened, finding the way.*
