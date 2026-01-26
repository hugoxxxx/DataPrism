# DataPrism 📸

**DataPrism** is a high-end metadata management studio designed for professional photographers. It bridges the gap between digital workflows and analog records, providing a specialized environment for batch EXIF editing, smart metadata mapping, and real-time process monitoring.

Inspired by premium imaging software like Hasselblad Phocus and Phase One Capture One, DataPrism offers a sleek "Studio Dark" aesthetic and a highly efficient, professional-grade interface.

![Main Interface Mockup](https://via.placeholder.com/1200x800/101012/D15400?text=DataPrism+Studio+Dark+UI)

## 🌟 Key Features

- **Studio-Grade UI**: A premium dark-mode interface optimized for high-end photography workflows.
- **Batch Metadata Injection**: Seamlessly write camera brand, lens model, film stock, and exposure data to thousands of photos simultaneously using the **ExifTool** engine.
- **Smart Data Mapping**: Import your shooting logs (CSV/JSON/TXT) and use "Smart Match" to correlate shooting data with your digital scans.
- **Quick Write Panel**: Rapidly apply common metadata to selected photos or entire roll.
- **Real-time Process Console**: A professional execution log providing full transparency for background technical operations.
- **Cross-Era Metadata**: Specialized support for film photographers to record Camera, Lens, and Film Stock that traditional digital workflows often lack.
- **Multi-language Support**: Full internationalization for English and Chinese (Simplified).

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- [ExifTool](https://exiftool.org/) installed and in your system PATH.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/DataPrism.git
   cd DataPrism
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
```bash
python main.py
```

## 🛠️ Performance & Tech
- **Core Engine**: PySide6 (Qt for Python).
- **Metadata Handler**: Phil Harvey's ExifTool.
- **Design System**: Decoupled JSON-based theme management.

## 📄 License
MIT License - Copyright (c) 2026 DataPrism Team

---
*Elevate your metadata, streamline your vision.*
