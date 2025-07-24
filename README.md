# Minesweeper Game

A modern, responsive implementation of the classic Minesweeper game built with vanilla HTML, CSS, and JavaScript.

## Features

- **Three Difficulty Levels**
  - Easy: 9×9 grid with 10 mines
  - Medium: 16×16 grid with 40 mines
  - Hard: 16×30 grid with 99 mines

- **Game Mechanics**
  - Left-click to reveal cells
  - Right-click to flag/unflag suspected mines
  - First click is always safe (mines placed after first click)
  - Flood fill algorithm reveals connected empty cells
  - Timer tracks game duration
  - Mine counter shows remaining unflagged mines

- **Modern UI/UX**
  - Responsive design for desktop, tablet, and mobile
  - Gradient background with card-based layout
  - Interactive hover effects and animations
  - Color-coded numbers for mine proximity (1-8)
  - Visual feedback for game states (playing, won, lost)

- **Game States**
  - Ready: Initial state before first click
  - Playing: Active gameplay with running timer
  - Won: All safe cells revealed, mines auto-flagged
  - Lost: Mine clicked, all mines revealed

## How to Play

1. **Start**: Click any cell to begin the game
2. **Reveal**: Left-click cells to reveal them
3. **Flag**: Right-click cells to mark suspected mines
4. **Numbers**: Revealed numbers indicate adjacent mine count
5. **Win**: Reveal all safe cells without clicking mines
6. **Reset**: Click the smiley button to start over

## Technical Implementation

- **Object-Oriented Design**: Clean Minesweeper class structure
- **Responsive Grid**: CSS Grid for flexible board layouts
- **Event Handling**: Mouse events for cell interactions
- **State Management**: Comprehensive game state tracking
- **Algorithm Efficiency**: Optimized flood fill and mine placement

## File Structure

```
minesweeper/
├── index.html      # HTML structure and layout
├── style.css       # Styling and responsive design
├── script.js       # Game logic and interactions
└── README.md       # Project documentation
```

## Browser Compatibility

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## Getting Started

1. Clone or download the project files
2. Open `index.html` in a web browser
3. Start playing immediately - no build process required!

## Game Controls

- **Left Click**: Reveal cell
- **Right Click**: Toggle flag
- **Reset Button**: Start new game
- **Difficulty Buttons**: Change game difficulty

Enjoy the classic Minesweeper experience with a modern twist!
