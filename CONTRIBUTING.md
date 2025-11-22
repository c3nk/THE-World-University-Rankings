# Katkıda Bulunma Rehberi / Contributing Guide

🇹🇷 [Türkçe](#türkçe) | 🇬🇧 [English](#english)

---

## Türkçe

THE World University Rankings Scraper projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu rehber, katkıda bulunma sürecini kolaylaştırmak için hazırlanmıştır.

### 📋 İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunurum?](#nasıl-katkıda-bulunurum)
- [Hata Bildirme](#hata-bildirme)
- [Özellik Önerme](#özellik-önerme)
- [Kod Katkısı](#kod-katkısı)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Kod Standartları](#kod-standartları)
- [Commit Mesajları](#commit-mesajları)
- [Pull Request Süreci](#pull-request-süreci)

### 🤝 Davranış Kuralları

Bu projeye katılan herkes:
- Saygılı ve yapıcı iletişim kurar
- Farklı bakış açılarına açık olur
- Yapıcı eleştiri yapar ve kabul eder
- Topluluk çıkarlarını ön planda tutar
- Diğer katkıda bulunanlara empati gösterir

### 💡 Nasıl Katkıda Bulunurum?

Katkıda bulunmanın birçok yolu vardır:

1. **🐛 Hata bildirimi** - Bulduğunuz hataları bildirin
2. **💭 Özellik önerisi** - Yeni fikirlerinizi paylaşın
3. **📝 Dokümantasyon** - Dokümantasyonu iyileştirin
4. **🔧 Kod katkısı** - Hataları düzeltin veya yeni özellikler ekleyin
5. **🌍 Çeviri** - Dokümantasyon çevirilerine katkıda bulunun
6. **⭐ Yıldız verme** - Projeye yıldız vererek destek olun

### 🐛 Hata Bildirme

Bir hata bulduğunuzda:

1. **Önce kontrol edin**: [Issues](https://github.com/c3nk/THE-World-University-Rankings/issues) sayfasında aynı sorunun daha önce bildirilip bildirilmediğini kontrol edin
2. **Yeni issue açın**: Eğer yoksa, yeni bir issue açın
3. **Detaylı açıklama yapın**:
   - Hatanın ne olduğunu açıklayın
   - Hatayı nasıl tekrar oluşturabileceğinizi anlatın
   - Beklenen davranış neydi?
   - Ekran görüntüsü ekleyin (varsa)
   - Ortam bilgilerinizi paylaşın (Python versiyonu, işletim sistemi vb.)

**Hata bildirimi şablonu:**

```markdown
## Hata Açıklaması
Hatanın kısa ve net açıklaması.

## Tekrar Üretme Adımları
1. '...' komutunu çalıştırın
2. '...' dosyasını açın
3. Hatayı görün

## Beklenen Davranış
Ne olmasını bekliyordunuz?

## Ekran Görüntüleri
Varsa ekleyin.

## Ortam
- Python versiyonu: [örn. 3.9.5]
- İşletim sistemi: [örn. Ubuntu 20.04]
- Proje versiyonu: [örn. v1.0.0]

## Ek Bağlam
Başka eklemek istediğiniz bilgi.
```

### 💭 Özellik Önerme

Yeni bir özellik önermek için:

1. **Issue açın**: Başlığa `[Özellik]` veya `[Feature]` ekleyin
2. **Detaylı açıklama yapın**:
   - Özellik neden gerekli?
   - Nasıl çalışmalı?
   - Hangi kullanım senaryolarında faydalı olur?
   - Varsa benzer örnekler gösterin

**Özellik önerisi şablonu:**

```markdown
## Özellik Açıklaması
Özelliğin ne olduğunu açıklayın.

## Motivasyon
Bu özellik neden gerekli? Hangi sorunu çözüyor?

## Önerilen Çözüm
Özelliğin nasıl çalışmasını istiyorsunuz?

## Alternatifler
Düşündüğünüz başka çözümler var mı?

## Ek Bağlam
Başka eklemek istediğiniz bilgi.
```

### 🔧 Kod Katkısı

Kod katkısında bulunmak için:

1. **Forklayın**: Projeyi kendi hesabınıza forklayın
2. **Clone edin**: Forkladığınız projeyi bilgisayarınıza indirin
   ```bash
   git clone https://github.com/KULLANICI_ADINIZ/THE-World-University-Rankings.git
   ```
3. **Branch oluşturun**: Yeni bir branch oluşturun
   ```bash
   git checkout -b feature/yeni-ozellik
   ```
4. **Değişiklik yapın**: Kodunuzu yazın
5. **Test edin**: Değişikliklerinizi test edin
6. **Commit yapın**: Değişikliklerinizi commit edin
   ```bash
   git commit -m "feat: yeni özellik eklendi"
   ```
7. **Push yapın**: Branch'inizi GitHub'a gönderin
   ```bash
   git push origin feature/yeni-ozellik
   ```
8. **Pull Request açın**: GitHub'da pull request oluşturun

### ⚙️ Geliştirme Ortamı Kurulumu

```bash
# Projeyi klonlayın
git clone https://github.com/c3nk/THE-World-University-Rankings.git
cd THE-World-University-Rankings

# Sanal ortam oluşturun
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Test çalıştırması yapın
python the_world_university_rankings_scraper.py
```

### 📝 Kod Standartları

- **PEP 8**: Python kod stiline uyun
- **Dokümantasyon**: Fonksiyonlara docstring ekleyin
- **Değişken isimleri**: Açıklayıcı isimler kullanın
- **Yorum satırları**: Karmaşık kod bloklarını açıklayın
- **Hata yönetimi**: Try-except blokları kullanın

**Örnek kod stili:**

```python
def fetch_ranking_data(year: int) -> dict:
    """
    Belirtilen yıl için THE sıralama verilerini çeker.
    
    Args:
        year (int): Sıralama yılı (2011-2026)
    
    Returns:
        dict: Sıralama verileri
    
    Raises:
        ValueError: Geçersiz yıl değeri
        requests.RequestException: API isteği başarısız
    """
    if year < 2011 or year > 2026:
        raise ValueError(f"Geçersiz yıl: {year}")
    
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"API hatası: {e}")
```

### 📋 Commit Mesajları

Commit mesajlarınız için [Conventional Commits](https://www.conventionalcommits.org/) standardını kullanın:

- `feat:` - Yeni özellik
- `fix:` - Hata düzeltme
- `docs:` - Dokümantasyon değişikliği
- `style:` - Kod formatı (kod davranışını değiştirmeyen)
- `refactor:` - Kod yeniden yapılandırma
- `test:` - Test ekleme veya düzeltme
- `chore:` - Bakım işleri

**Örnek commit mesajları:**

```bash
feat: 2027 yılı veri desteği eklendi
fix: CSV çıktısında karakter kodlaması hatası düzeltildi
docs: README'ye kullanım örneği eklendi
refactor: API istek fonksiyonları yeniden yapılandırıldı
```

### 🔀 Pull Request Süreci

1. **Açıklayıcı başlık**: PR'ınıza açıklayıcı bir başlık verin
2. **Detaylı açıklama**: Neler yaptığınızı açıklayın
   - Hangi sorunu çözüyor?
   - Nasıl test edildi?
   - Ekran görüntüleri (varsa)
3. **Issue bağlantısı**: İlgili issue'yu bağlayın
4. **Değişiklik listesi**: Yaptığınız değişiklikleri listeleyin
5. **Testler**: Kodunuzun çalıştığını doğrulayın

**PR şablonu:**

```markdown
## Açıklama
Bu PR'ın amacını açıklayın.

## İlgili Issue
Fixes #123

## Değişiklikler
- [ ] Özellik 1 eklendi
- [ ] Hata 2 düzeltildi
- [ ] Dokümantasyon güncellendi

## Test Edildi Mi?
- [ ] Evet, yerel ortamda test edildi
- [ ] Tüm testler başarılı

## Ekran Görüntüleri
Varsa ekleyin.

## Checklist
- [ ] Kod PEP 8 standartlarına uygun
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md güncellendi (önemliyse)
```

### ✅ İnceleme Süreci

Pull request'iniz:
1. Otomatik testlerden geçecek (varsa)
2. Proje sahipleri tarafından incelenecek
3. Gerekirse değişiklik talepleri alacak
4. Onaylandıktan sonra merge edilecek

### 🎉 Katkıda Bulunanlar

Tüm katkıda bulunanlara teşekkür ederiz! Katkınız projeyi daha iyi hale getiriyor.

### 📞 İletişim

Sorularınız için:
- **GitHub Issues**: Teknik sorular için
- **GitHub Discussions**: Genel tartışmalar için

---

## English

Thank you for considering contributing to THE World University Rankings Scraper! This guide will help make the contribution process smooth and effective.

### 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Code Contribution](#code-contribution)
- [Development Environment Setup](#development-environment-setup)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

### 🤝 Code of Conduct

All participants in this project should:
- Communicate respectfully and constructively
- Be open to different perspectives
- Give and accept constructive criticism
- Prioritize community interests
- Show empathy towards other contributors

### 💡 How Can I Contribute?

There are many ways to contribute:

1. **🐛 Bug reports** - Report bugs you find
2. **💭 Feature requests** - Share your ideas
3. **📝 Documentation** - Improve documentation
4. **🔧 Code contributions** - Fix bugs or add features
5. **🌍 Translations** - Contribute to documentation translations
6. **⭐ Star the project** - Support by starring

### 🐛 Reporting Bugs

When you find a bug:

1. **Check first**: Look at [Issues](https://github.com/c3nk/THE-World-University-Rankings/issues) to see if it's already reported
2. **Open new issue**: If not found, create a new issue
3. **Provide details**:
   - Describe what the bug is
   - Explain how to reproduce it
   - What was the expected behavior?
   - Add screenshots (if applicable)
   - Share your environment (Python version, OS, etc.)

**Bug report template:**

```markdown
## Bug Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Run '...' command
2. Open '...' file
3. See error

## Expected Behavior
What did you expect to happen?

## Screenshots
If applicable, add screenshots.

## Environment
- Python version: [e.g. 3.9.5]
- Operating system: [e.g. Ubuntu 20.04]
- Project version: [e.g. v1.0.0]

## Additional Context
Any other relevant information.
```

### 💭 Suggesting Features

To suggest a new feature:

1. **Open an issue**: Add `[Feature]` to the title
2. **Provide details**:
   - Why is this feature needed?
   - How should it work?
   - What use cases does it address?
   - Show similar examples if available

**Feature request template:**

```markdown
## Feature Description
Describe what the feature is.

## Motivation
Why is this feature needed? What problem does it solve?

## Proposed Solution
How would you like this feature to work?

## Alternatives
Any alternative solutions you've considered?

## Additional Context
Any other relevant information.
```

### 🔧 Code Contribution

To contribute code:

1. **Fork**: Fork the project to your account
2. **Clone**: Clone your fork locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/THE-World-University-Rankings.git
   ```
3. **Create branch**: Create a new branch
   ```bash
   git checkout -b feature/new-feature
   ```
4. **Make changes**: Write your code
5. **Test**: Test your changes
6. **Commit**: Commit your changes
   ```bash
   git commit -m "feat: add new feature"
   ```
7. **Push**: Push your branch to GitHub
   ```bash
   git push origin feature/new-feature
   ```
8. **Open PR**: Create a pull request on GitHub

### ⚙️ Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/c3nk/THE-World-University-Rankings.git
cd THE-World-University-Rankings

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run test
python the_world_university_rankings_scraper.py
```

### 📝 Code Standards

- **PEP 8**: Follow Python style guide
- **Documentation**: Add docstrings to functions
- **Variable names**: Use descriptive names
- **Comments**: Explain complex code blocks
- **Error handling**: Use try-except blocks

**Example code style:**

```python
def fetch_ranking_data(year: int) -> dict:
    """
    Fetch THE ranking data for specified year.
    
    Args:
        year (int): Ranking year (2011-2026)
    
    Returns:
        dict: Ranking data
    
    Raises:
        ValueError: Invalid year value
        requests.RequestException: API request failed
    """
    if year < 2011 or year > 2026:
        raise ValueError(f"Invalid year: {year}")
    
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"API error: {e}")
```

### 📋 Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) standard:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code formatting (no behavior change)
- `refactor:` - Code restructuring
- `test:` - Adding or fixing tests
- `chore:` - Maintenance tasks

**Example commit messages:**

```bash
feat: add support for 2027 data
fix: resolve CSV output encoding issue
docs: add usage example to README
refactor: restructure API request functions
```

### 🔀 Pull Request Process

1. **Descriptive title**: Give your PR a clear title
2. **Detailed description**: Explain what you did
   - What problem does it solve?
   - How was it tested?
   - Screenshots (if applicable)
3. **Link issue**: Reference related issue
4. **Change list**: List your changes
5. **Tests**: Verify your code works

**PR template:**

```markdown
## Description
Explain the purpose of this PR.

## Related Issue
Fixes #123

## Changes
- [ ] Added feature 1
- [ ] Fixed bug 2
- [ ] Updated documentation

## Tested?
- [ ] Yes, tested locally
- [ ] All tests pass

## Screenshots
If applicable, add screenshots.

## Checklist
- [ ] Code follows PEP 8 standards
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if significant)
```

### ✅ Review Process

Your pull request will:
1. Go through automated tests (if available)
2. Be reviewed by project maintainers
3. Receive change requests if needed
4. Be merged after approval

### 🎉 Contributors

Thank you to all contributors! Your contributions make this project better.

### 📞 Contact

For questions:
- **GitHub Issues**: For technical questions
- **GitHub Discussions**: For general discussions

---

<div align="center">

**Thank you for contributing! / Katkılarınız için teşekkürler!** ❤️

</div>