<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Skimo Equipment Guide</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background-color: #0f172a;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 24px;
    }
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .lang-select {
      background: #1e293b;
      color: #38bdf8;
      border: 1px solid #334155;
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: bold;
      cursor: pointer;
    }
    .grid-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
    }
    .card {
      background-color: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .card-content {
      padding: 20px;
      flex: 1;
    }
    .card-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 12px;
    }
    .card-desc {
      font-size: 0.9rem;
      color: #94a3b8;
      line-height: 1.6;
    }
    .card-img-wrapper {
      width: 100%;
      height: 220px;
      background-color: #0f172a;
      position: relative;
    }
    .card-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .img-caption {
      position: absolute;
      bottom: 0;
      width: 100%;
      background: rgba(15, 23, 42, 0.8);
      color: #cbd5e1;
      text-align: center;
      padding: 6px;
      font-size: 0.8rem;
    }
  </style>
</head>
<body>

  <div class="header-bar">
    <h1 id="page-title">필수 장비 가이드</h1>
    <select id="lang-picker" class="lang-select" onchange="changeLanguage(this.value)">
      <option value="KO" selected>한국어 (KO)</option>
      <option value="EN">English (EN)</option>
      <option value="FR">Français (FR)</option>
      <option value="IT">Italiano (IT)</option>
      <option value="ZH">中文 (ZH)</option>
      <option value="JA">日本語 (JA)</option>
    </select>
  </div>

  <div class="grid-container" id="equipment-grid">
    <!-- 동적 카드 생성 영역 -->
  </div>

  <script>
    // 6개국어 완벽 통합 텍스트 정의
    const LOCALIZED_TEXT = {
      KO: {
        pageTitle: "필수 장비 가이드",
        items: [
          {
            title: "1. 초경량 산악스키 (Skimo Skis)",
            desc: "오르막길을 빠르게 뛰어 올라가야 하므로 일반 알파인 스키에 비해 상상할 수 없을 정도로 가볍습니다. 남성용 기준 최소 780g, 여성용 700g 선으로 제한되며 탄소 섬유(Carbon)로 제작됩니다.",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Light Skis"
          },
          {
            title: "2. 투어링 바인딩 (Tech Bindings)",
            desc: "산악스키 바인딩은 업힐 모드 시 뒷굽이 떨어져 걸어 올라갈 수 있게 설계되었습니다. 다운힐 모드 시에는 뒷굽을 고정합니다. 핀(Pin) 테크 방식을 채택해 무게가 겨우 100g 안팎입니다.",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Tech Binding System"
          },
          {
            title: "3. 등반용 클라이밍 스킨 (Climbing Skins)",
            desc: "스키 플레이트 바닥에 붙이는 모헤어(Mohair) 소재의 전용 스킨입니다. 앞방향으로는 미끄러지지만, 뒷방향으로는 털이 서서 눈을 움켜쥐기 때문에 미끄러지지 않고 수직 오르막을 오를 수 있습니다.",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Climbing Skins Setup"
          },
          {
            title: "4. 워크 모드 지원 부츠 (Skimo Boots)",
            desc: "레버 하나로 발목 관절 구동 범위를 60도 이상 확보하는 '워크 모드'와 활강을 위해 고정하는 '스키 모드'를 전환할 수 있습니다. 경량화를 위해 카본 셸을 적극 활용합니다.",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Ultralight Skimo Boots"
          },
          {
            title: "5. 탄소섬유 카본 폴 (Carbon Poles)",
            desc: "상체 반동과 팔 근육을 이용해 업힐 추진력을 내는 도구입니다. 일반 스키 폴보다 길며, 샤프트 전체가 100% High-Modulus Carbon으로 제작되어 극강의 경량성을 확보합니다.",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Fiber Touring Poles"
          }
        ]
      },
      EN: {
        pageTitle: "Essential Gear Guide",
        items: [
          {
            title: "1. Ultralight Skimo Skis",
            desc: "Designed to be exceptionally lightweight for fast uphill ascents compared to alpine skis. Minimum weight is restricted around 780g for men and 700g for women, crafted with high-grade carbon fiber.",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Light Skis"
          },
          {
            title: "2. Tech Bindings",
            desc: "Skimo bindings feature a free-heel design during uphill mode for climbing. For downhill, the heel locks securely. Using pin-tech design, they weigh around 100g.",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Tech Binding System"
          },
          {
            title: "3. Climbing Skins",
            desc: "Mohair skins attached to the bottom of ski bases. They glide smoothly forward while gripping snow backward, enabling steep vertical climbs.",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Climbing Skins Setup"
          },
          {
            title: "4. Skimo Boots",
            desc: "Features a single lever to switch between 'Walk Mode' offering over 60 degrees range of motion and locked 'Ski Mode' for downhill control.",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Ultralight Skimo Boots"
          },
          {
            title: "5. Carbon Fiber Poles",
            desc: "Poles provide uphill propulsion using upper body strength. Longer than alpine poles, constructed with 100% High-Modulus Carbon for extreme lightness.",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Fiber Touring Poles"
          }
        ]
      },
      FR: {
        pageTitle: "Guide Matériel Essentiel",
        items: [
          {
            title: "1. Skis de Randonnée Ultra-Légers",
            desc: "Conçus pour être extrêmement légers lors des montées rapides. Limite de poids minimale à 780g (hommes) et 700g (femmes), fabriqués en fibre de carbone.",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Skis Legers en Carbone"
          },
          {
            title: "2. Fixations Tech",
            desc: "Libèrent le talon en mode montée et le verrouillent pour la descente. Grâce au système à inserts (pins), elles ne pèsent qu'environ 100g.",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Système de Fixation Tech"
          },
          {
            title: "3. Peaux de Phoque",
            desc: "Peaux en mohair fixées sous les skis. Elles glissent vers l'avant et accrochent la neige vers l'arrière pour gravir les pentes raides.",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Installation Peaux de Phoque"
          },
          {
            title: "4. Chaussures de Skimo",
            desc: "Basculez entre le 'Mode Marche' (+60° de débattement) et le 'Mode Ski' verrouillé via un seul levier ergonomique.",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Chaussures Skimo Ultra-Légères"
          },
          {
            title: "5. Bâtons en Carbone",
            desc: "Offrent une propulsion efficace à la montée. Plus longs que les bâtons alpins, entièrement faits en carbone High-Modulus.",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Bâtons de Randonnée Carbone"
          }
        ]
      },
      IT: {
        pageTitle: "Guida Attrezzatura Essenziale",
        items: [
          {
            title: "1. Sci da Sci Alpinismo Ultra-Leggeri",
            desc: "Progettati per la massima leggerezza nelle salite veloci. Peso minimo di 780g per gli uomini e 700g per le donne, realizzati in fibra di carbonio.",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Sci Leggeri in Carbonio"
          },
          {
            title: "2. Attacchi Tech",
            desc: "Sbloccano il tallone per la salita e lo bloccano per la discesa. Utilizzano la tecnologia a pin con un peso ridotto a circa 100g.",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Sistema Attacchi Tech"
          },
          {
            title: "3. Pelli di Foca",
            desc: "Pelli in mohair applicate sotto la soletta. Scivolano in avanti e fanno presa sulla neve all'indietro per le salite più ripide.",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Set Pelli di Foca"
          },
          {
            title: "4. Scarponi da Skimo",
            desc: "Un'unica leva permette di passare dalla 'Modalità Camminata' (oltre 60° di rotazione) alla 'Modalità Sci' per la discesa.",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Scarponi Skimo Ultra-Leggeri"
          },
          {
            title: "5. Bastoncini in Carbonio",
            desc: "Forniscono la spinta necessaria in salita. Più lunghi dei normali bastoncini, costituiti al 100% da carbonio High-Modulus.",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Bastoncini in Carbonio"
          }
        ]
      },
      ZH: {
        pageTitle: "必备装备指南",
        items: [
          {
            title: "1. 超轻登山滑雪板 (Skimo Skis)",
            desc: "为了能够快速冲顶，设计比普通高山滑雪板轻盈得多。男款限制重量至少780克，女款700克，采用全碳纤维打造。",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Light Skis"
          },
          {
            title: "2. 巡回固定器 (Tech Bindings)",
            desc: "攀登模式下脚后跟可分离以便行走，滑降模式下可锁定后跟。采用针式(Pin)技术，重量仅100克左右。",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Tech Binding System"
          },
          {
            title: "3. 登山雪贴/止滑皮 (Climbing Skins)",
            desc: "贴在雪板底部的马海毛(Mohair)材质防滑皮。向前滑动顺畅，向后倒退时逆毛抓雪，可顺利进行垂直攀登。",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Climbing Skins Setup"
          },
          {
            title: "4. 行走模式雪靴 (Skimo Boots)",
            desc: "通过单个控制杆即可在脚踝活动度达60度以上的'行走模式'和固定下滑的'滑雪模式'之间自由切换。",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Ultralight Skimo Boots"
          },
          {
            title: "5. 碳纤维雪杖 (Carbon Poles)",
            desc: "利用上半身反弹力和手臂力量提供上坡推进力。比普通雪杖更长，杖身采用100%高模量碳纤维制作，极致轻量。",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Fiber Touring Poles"
          }
        ]
      },
      JA: {
        pageTitle: " mandatory 必須ギアガイド",
        items: [
          {
            title: "1. 超軽量山岳スキー (Skimo Skis)",
            desc: "登坂を素早く登るため、一般的なアルペンスキーに比べて非常に軽量です。男性用最低780g、女性用700g程度に制限され、カーボンファイバーで製作されます。",
            img: "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Light Skis"
          },
          {
            title: "2. ツアービンディング (Tech Bindings)",
            desc: "アッパーモード時はヒールが離れて歩行でき、ダウンヒルモード時はヒールを固定します。ピン(Pin)テック方式を採用し重量はわずか100g前後です。",
            img: "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
            caption: "Tech Binding System"
          },
          {
            title: "3. 登坂用クライミングシール (Climbing Skins)",
            desc: "スキー滑走面につけるモヘア(Mohair)素材の専用シールです。前方向には滑り、後ろ方向には毛が立って雪を掴むため滑らずに登坂可能です。",
            img: "https://images.unsplash.com/photo-1548783307-e83c21a4fa8a?auto=format&fit=crop&w=800&q=80",
            caption: "Climbing Skins Setup"
          },
          {
            title: "4. ウォークモード対応ブーツ (Skimo Boots)",
            desc: "レバー1つで足首の可動域を60度以上確保する「ウォークモード」と滑走用の「スキーモード」を切り替えられます。",
            img: "https://images.unsplash.com/photo-1517649763962-0c6232662000?auto=format&fit=crop&w=800&q=80",
            caption: "Ultralight Skimo Boots"
          },
          {
            title: "5. カーボンファイバーポール (Carbon Poles)",
            desc: "上半身と腕の muscle を利用して登坂の推進力を生み出します。通常のポールより長く、シャフト全体が100% High-Modulus Carbonで極限の軽量性を実現しています。",
            img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
            caption: "Carbon Fiber Touring Poles"
          }
        ]
      }
    };

    let currentLang = "KO";

    function renderUI() {
      const langData = LOCALIZED_TEXT[currentLang] || LOCALIZED_TEXT["KO"];
      
      // 타이틀 업데이트
      document.getElementById("page-title").innerText = langData.pageTitle;

      // 카드 리스트 동적 렌더링
      const gridContainer = document.getElementById("equipment-grid");
      gridContainer.innerHTML = "";

      langData.items.forEach(item => {
        const cardHTML = `
          <div class="card">
            <div class="card-content">
              <div class="card-title">${item.title}</div>
              <div class="card-desc">${item.desc}</div>
            </div>
            <div class="card-img-wrapper">
              <img class="card-img" src="${item.img}" alt="${item.title}" loading="lazy" />
              <div class="img-caption">${item.caption}</div>
            </div>
          </div>
        `;
        gridContainer.insertAdjacentHTML("beforeend", cardHTML);
      });
    }

    function changeLanguage(lang) {
      currentLang = lang;
      renderUI();
    }

    // 초기 실행
    renderUI();
  </script>
</body>
</html>
