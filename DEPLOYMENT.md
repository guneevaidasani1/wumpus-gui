# Wumpus World - GitHub Pages Deployment Guide

## 🌐 Deploy to GitHub Pages (Play in Browser!)

Your game is now configured to run in the browser using **Pygbag**. Follow these steps:

### Step 1: Push to GitHub

```bash
cd c:\Users\gunee\Documents\wumpus-world-main-gui

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Add web deployment with Pygbag"

# Add your GitHub repo (create it first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/wumpus-world-main-gui.git

# Push to GitHub
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

### Step 3: Wait for Deployment

- GitHub will build your site (takes 1-2 minutes)
- Your game will be live at: `https://YOUR_USERNAME.github.io/wumpus-world-main-gui/`

### Step 4: Share Your Game! 🎮

Once deployed, anyone can play your game in their browser by visiting your GitHub Pages URL!

## 🔧 How It Works

- **index.html** - The web page that hosts your game
- **pygbag.ini** - Configuration for Pygbag (web packaging)
- **Pygbag** - Converts your Pygame code to run in the browser using WebAssembly

## 📝 Notes

- The game runs entirely in the browser (no installation needed)
- Players can use all the same controls (WASD, arrows, etc.)
- Fullscreen (F11) works in the browser too!
- The cave theme and all visual effects are preserved

## 🎨 Customization

### Update the GitHub Link in index.html

Open `index.html` and replace:
```html
<a href="https://github.com/yourusername/wumpus-world-main-gui" target="_blank">
```

With your actual GitHub username.

### Change Colors/Styling

Edit the `<style>` section in `index.html` to customize the web page appearance.

## 🐛 Troubleshooting

**Game not loading?**
- Check browser console (F12) for errors
- Make sure GitHub Pages is enabled
- Wait a few minutes after pushing changes

**Controls not working?**
- Click on the game canvas first
- Some browsers require user interaction before starting

**Performance issues?**
- The web version may be slightly slower than desktop
- Try a different browser (Chrome/Firefox recommended)

---

**Your game is ready to share with the world! 🚀**
