const menuButton = document.querySelector(".menu-btn");
const navigation = document.querySelector("nav");

const onepageApp = document.querySelector("#onepageApp");

// 메인 상단에서는 영상과 헤더를 자연스럽게 연결하고,
// 스크롤을 내리면 검은 헤더를 상단에 고정합니다.
const siteHeader = document.querySelector("header");

function updateHeaderOnScroll() {
  if (!siteHeader) return;
  const isHome = document.body.dataset.page === "home";
  siteHeader.classList.toggle("is-scrolled", isHome && window.scrollY > 90);
  document.documentElement.classList.toggle("home-scroll-snap", isHome);
}

window.addEventListener("scroll", updateHeaderOnScroll, { passive: true });

function showOnepageView(viewName, updateHistory = true) {
  if (!onepageApp) return;
  const fallback = document.querySelector('[data-view="home"].spa-view');
  const target = document.querySelector(`.spa-view[data-view="${viewName}"]`) || fallback;
  if (!target) return;
  document.querySelectorAll(".spa-view").forEach((view) => view.classList.remove("active"));
  target.classList.add("active");
  document.body.dataset.page = target.dataset.view;
  updateHeaderOnScroll();
  document.querySelectorAll("header nav a").forEach((link) => {
    link.classList.toggle("current", link.dataset.view === target.dataset.view);
  });
  navigation?.classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (updateHistory) history.pushState({ view: target.dataset.view }, "", `#${target.id}`);
}

document.querySelectorAll(".spa-link[data-view]").forEach((link) => {
  link.addEventListener("click", (event) => {
    if (!onepageApp || event.metaKey || event.ctrlKey) return;
    event.preventDefault();
    showOnepageView(link.dataset.view);
  });
});

if (onepageApp) {
  const hashView = location.hash.replace("#", "");
  showOnepageView(hashView || onepageApp.dataset.initialView || "home", false);
  window.addEventListener("popstate", () => {
    showOnepageView(location.hash.replace("#", "") || "home", false);
  });
}

updateHeaderOnScroll();

// 500px 아래에서만 나타나는 공통 TOP 버튼
const pageTopButton = document.createElement("button");
pageTopButton.type = "button";
pageTopButton.className = "page-top-button";
pageTopButton.textContent = "TOP";
pageTopButton.setAttribute("aria-label", "페이지 맨 위로 이동");
document.body.appendChild(pageTopButton);

function updatePageTopButton() {
  pageTopButton.classList.toggle("is-visible", window.scrollY >= 500);
}

window.addEventListener("scroll", updatePageTopButton, { passive: true });
pageTopButton.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
updatePageTopButton();

if (menuButton) {
  menuButton.addEventListener("click", () => {
    const isOpen = navigation.classList.toggle("open");
    menuButton.classList.toggle("is-open", isOpen);
    menuButton.setAttribute("aria-expanded", String(isOpen));
  });
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add("show");
  });
}, { threshold: 0.08 });

document.querySelectorAll(".section, .genre-row").forEach((element) => {
  observer.observe(element);
});

const videoFilterButtons = document.querySelectorAll(".video-filter button");
videoFilterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    videoFilterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelectorAll(".video-card").forEach((card) => {
      card.style.display =
        button.textContent === "전체" || card.dataset.genre === button.textContent
          ? "block"
          : "none";
    });
  });
});

const modal = document.querySelector("#videoModal");
const previewVideo = document.querySelector("#previewVideo");
const videoTitle = document.querySelector("#videoTitle");
const videoHelp = document.querySelector("#videoHelp");

function closeVideoModal() {
  if (!modal) return;
  previewVideo.pause();
  previewVideo.removeAttribute("src");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
}

document.querySelectorAll(".preview-trigger").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();

    const card = button.closest(".video-card");
    if (!card || !modal || !previewVideo) return;
    if (!card.dataset.video) {
      window.alert("이 도서는 아직 제작된 프리뷰 영상이 없습니다.");
      return;
    }

    videoTitle.textContent = `${card.dataset.title} 프리뷰`;
    previewVideo.src = card.dataset.video;
    videoHelp.textContent = "영상 파일을 불러오는 중입니다.";
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    previewVideo.play().catch(() => {});
  });
});

// 프리뷰 카드 안의 상세보기는 영상 팝업과 분리하여 상세 화면으로 이동합니다.
document.querySelectorAll(".detail-link").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.stopPropagation();
  });
});

if (modal) {
  modal.querySelector(".modal-close").addEventListener("click", closeVideoModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeVideoModal();
  });
}

if (previewVideo) {
  previewVideo.addEventListener("loadeddata", () => {
    videoHelp.textContent = "영상 재생 준비가 완료되었습니다.";
  });
  previewVideo.addEventListener("error", () => {
    videoHelp.textContent =
      "영상 파일이 아직 없습니다. static/videos 폴더에 book1.mp4부터 book8.mp4까지 넣어 주세요.";
  });
}

const easyButton = document.querySelector("#easyButton");
if (easyButton) {
  easyButton.addEventListener("click", async () => {
    const resultBox = document.querySelector("#easyResult");
    const easyColumns = document.querySelector("#easyColumns");
    const text = document.querySelector("#originalDescription").textContent.trim();
    const previewSection = document.querySelector("#previewSection");
    const aiImageLoading = document.querySelector("#aiImageLoading");
    const moodImage = document.querySelector("#moodImage");
    const imageStatus = document.querySelector("#imageStatus");
    previewSection.hidden = false;
    previewSection.classList.add("is-making");
    aiImageLoading.hidden = false;
    moodImage.hidden = true;
    previewSection.scrollIntoView({ behavior: "smooth", block: "center" });
    easyButton.disabled = true;
    easyButton.textContent = "바꾸는 중...";
    if (easyColumns) easyColumns.hidden = false;
    resultBox.textContent = "잠시만 기다려 주세요.";
    try {
      const response = await fetch("/api/ai-preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          book_key: easyButton.dataset.bookKey,
          text,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "AI 생성에 실패했습니다.");
      resultBox.textContent = data.ok ? data.easy_text : data.message;
      if (data.image_url) {
        moodImage.src = data.image_url;
        moodImage.onload = () => {
          aiImageLoading.hidden = true;
          moodImage.hidden = false;
          previewSection.classList.remove("is-making");
          previewSection.classList.add("is-complete");
        };
        imageStatus.textContent = data.cached
          ? "저장된 분위기 이미지를 불러왔습니다."
          : "FLUX가 책 소개를 바탕으로 만든 분위기 이미지입니다.";
      } else {
        aiImageLoading.hidden = true;
        previewSection.classList.remove("is-making");
        imageStatus.textContent = data.image_error || "이미지를 생성하지 못했습니다.";
      }
      if (data.gemini_error) {
        resultBox.textContent = data.gemini_error;
      }
    } catch (error) {
      resultBox.textContent = error.message || "연결에 실패했습니다. API 키와 인터넷 연결을 확인해 주세요.";
      aiImageLoading.hidden = true;
      previewSection.classList.remove("is-making");
      imageStatus.textContent = "이미지를 만들지 못했습니다. 잠시 후 다시 시도해 주세요.";
    } finally {
      easyButton.disabled = false;
      easyButton.textContent = "쉬운 글과 이미지 만들기";
    }
  });
}

const locateButton = document.querySelector("#locateButton");
if (locateButton) {
  const status = document.querySelector("#locationStatus");
  const placeList = document.querySelector("#placeList");
  const mapContainer = document.querySelector("#nearbyMap");
  const mapLink = document.querySelector("#largeMapLink");
  let kakaoMap;
  let placeService;
  let infoWindow;
  let markers = [];
  const setLocateLabel = (label) => {
    const labelNode = locateButton.querySelector("span");
    if (labelNode) labelNode.textContent = label;
  };

  const renderPlaces = (places) => {
    placeList.querySelectorAll(".place-card, .place-empty").forEach((item) => item.remove());
    if (!places.length) {
      const empty = document.createElement("div");
      empty.className = "place-empty";
      empty.textContent = "반경 5km 안에서 등록된 도서관이나 서점을 찾지 못했습니다.";
      placeList.appendChild(empty);
      return;
    }
    places.slice(0, 8).forEach((place) => {
      const article = document.createElement("article");
      article.className = "place-card";
      const type = place.category_name.includes("도서관") ? "도서관" : "서점";
      const icon = type === "도서관"
        ? `<span class="place-type-icon library-icon" aria-hidden="true"><img src="/static/images/icons/map/library.png" alt=""></span>`
        : `<span class="place-type-icon store-icon" aria-hidden="true"><img src="/static/images/icons/map/bookstore.png" alt=""></span>`;
      article.innerHTML =
        icon +
        `<div class="place-copy"><small>${type} · ${(Number(place.distance) / 1000).toFixed(1)}km</small><b></b><span></span></div>` +
        `<a target="_blank" rel="noopener">지도 ↗</a>`;
      article.querySelector("b").textContent = place.place_name;
      article.querySelector(".place-copy span").textContent = place.road_address_name || place.address_name;
      article.querySelector("a").href = place.place_url;
      placeList.appendChild(article);
    });
  };

  const searchNearby = (center) => {
    markers.forEach((marker) => marker.setMap(null));
    markers = [];
    const found = new Map();
    let completed = 0;
    const finish = () => {
      completed += 1;
      if (completed < 2) return;
      const places = [...found.values()].sort((a, b) => Number(a.distance) - Number(b.distance));
      places.forEach((place) => {
        const marker = new kakao.maps.Marker({ map: kakaoMap, position: new kakao.maps.LatLng(place.y, place.x) });
        kakao.maps.event.addListener(marker, "click", () => {
          infoWindow.setContent(`<div style="padding:8px 11px;white-space:nowrap;font-size:12px">${place.place_name}</div>`);
          infoWindow.open(kakaoMap, marker);
        });
        markers.push(marker);
      });
      renderPlaces(places);
      status.textContent = `현재 위치 주변에서 ${places.length}곳을 찾았습니다.`;
      locateButton.disabled = false;
      setLocateLabel("다시 찾기");
    };
    ["도서관", "서점"].forEach((keyword) => {
      placeService.keywordSearch(keyword, (data, searchStatus) => {
        if (searchStatus === kakao.maps.services.Status.OK) data.forEach((place) => found.set(place.id, place));
        finish();
      }, { location: center, radius: 5000, sort: kakao.maps.services.SortBy.DISTANCE });
    });
  };

  locateButton.addEventListener("click", () => {
    if (!window.kakao?.maps?.services) {
      status.textContent = "카카오 JavaScript 키를 .env의 KAKAO_MAP_APP_KEY에 입력해 주세요.";
      return;
    }
    if (!navigator.geolocation) {
      status.textContent = "이 브라우저에서는 위치 기능을 사용할 수 없습니다.";
      return;
    }
    locateButton.disabled = true;
    setLocateLabel("위치 확인 중...");
    status.textContent = "현재 위치를 확인하고 있습니다.";
    navigator.geolocation.getCurrentPosition(({ coords }) => {
      const latitude = coords.latitude;
      const longitude = coords.longitude;
      const center = new kakao.maps.LatLng(latitude, longitude);
      if (!kakaoMap) {
        kakaoMap = new kakao.maps.Map(mapContainer, { center, level: 5 });
        placeService = new kakao.maps.services.Places(kakaoMap);
        infoWindow = new kakao.maps.InfoWindow({ zIndex: 2 });
        kakaoMap.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
      } else {
        kakaoMap.setCenter(center);
      }
      new kakao.maps.Marker({ map: kakaoMap, position: center, title: "현재 위치" });
      mapLink.href = `https://map.kakao.com/link/map/현재 위치,${latitude},${longitude}`;
      status.textContent = "반경 5km 안의 도서관과 서점을 찾고 있습니다.";
      searchNearby(center);
    }, (error) => {
      const messages = {
        1: "위치 권한이 거부되었습니다. 주소창의 위치 권한을 허용해 주세요.",
        2: "현재 위치를 확인할 수 없습니다.",
        3: "위치 확인 시간이 초과되었습니다. 다시 시도해 주세요."
      };
      status.textContent = messages[error.code] || "위치를 확인하지 못했습니다.";
      locateButton.disabled = false;
      setLocateLabel("현재 위치로 찾기");
    }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 });
  });
}

const writeToggle = document.querySelector("#writeToggle");
if (writeToggle) {
  const postForm = document.querySelector("#postForm");
  const listFilters = document.querySelector("#communityListFilters");
  const toggleLabel = writeToggle.querySelector("span");
  const toolbar = writeToggle.closest(".community-toolbar");

  writeToggle.addEventListener("click", () => {
    const isOpen = postForm.classList.toggle("open");

    listFilters?.classList.toggle("is-hidden", isOpen);
    toolbar?.classList.toggle("writing", isOpen);
    writeToggle.classList.toggle("is-open", isOpen);
    writeToggle.setAttribute("aria-expanded", String(isOpen));
    postForm.setAttribute("aria-hidden", String(!isOpen));

    if (toggleLabel) {
      toggleLabel.textContent = isOpen ? "× 닫기" : "글쓰기";
    }
  });
}

document.querySelectorAll(".comment-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    button.parentElement.querySelector(".community-comments").classList.toggle("open");
  });
});
