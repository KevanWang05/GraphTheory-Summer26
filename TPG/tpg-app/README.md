# TPG Simulator

This a web app to simulate the TPG. It's primary use is for people unfamiliar with the game to become familiar.

sigma out

## Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run the Flask server
python app.py
```

Then open your browser at **http://127.0.0.1:5000**

## Usage

1. **Pick a graph** from the dropdown (complete, cycle, path, star, grid, etc.)
2. **Set q** using the slider or number input (0 – 1)
3. **Enter initial B nodes** as comma-separated node IDs (e.g. `0, 2, 5`)
4. Click **Initialise** to build the graph — green nodes = State A, red = State B
5. Use **Step** to advance one turn at a time, or **Play** to animate automatically
6. Adjust the **Speed** slider to control auto-play interval (100 ms – 2000 ms)
7. The simulation stops automatically when a fixed point or 2-period cycle is detected

## File Structure

```
tpg-app/
├── app.py            # Flask server & API endpoints
├── tpg.py            # TPG simulation class
├── requirements.txt
├── README.md
└── static/
    ├── index.html
    ├── style.css
    └── main.js
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/presets` | List available graph presets |
| POST | `/init` | Initialise simulation (`preset`, `q`, `initial_b`) |
| POST | `/step` | Advance one turn, returns new node states |
