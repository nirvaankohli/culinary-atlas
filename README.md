# Culinary Atlas

Ever wondered how different cultures make the same dish? This project helps you explore that.

Enter any dish name and get back cultural variations from around the world. Each variation includes the full recipe with ingredients, instructions, and the original source.

## What It Does

- Search for any dish (pizza, curry, dumplings, etc.)
- Get cultural variations with confidence ratings
- View detailed recipes with step-by-step instructions
- See where each recipe came from

## Setup

```bash
pip install -r requirements.txt
```

Run the app:
```bash
python app.py
```

Open http://localhost:5000

## How It Works

The backend uses two agents:
1. **Diversifier** - finds cultural variations of dishes
2. **Recipes** - fetches detailed recipe data

Results are stored locally in `data/db/` as JSON files.

## Built With

- Flask (backend)
- Vanilla JS (frontend)
- Custom CSS with animations
- JSON streaming for real-time updates

## License

MIT - see LICENSE file