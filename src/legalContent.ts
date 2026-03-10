import type { Language } from "./types";

export type LegalDocumentId = "privacy" | "terms";

interface LegalSection {
  id: string;
  title: string;
  paragraphs: string[];
  bullets?: string[];
}

export interface LegalDocumentContent {
  title: string;
  summary: string;
  lastUpdated: string;
  sections: LegalSection[];
}

export interface LegalUiCopy {
  sectionTitle: string;
  lead: string;
  privacyLinkLabel: string;
  termsLinkLabel: string;
  backToAbout: string;
  lastUpdatedLabel: string;
  footerPrivacy: string;
  footerTerms: string;
  fallbackNotice: string;
}

const LEGAL_UI_COPY: Partial<Record<Language, LegalUiCopy>> = {
  "en-US": {
    sectionTitle: "Legal",
    lead: "Pink Hunter now includes a site privacy policy and a plain-language terms and disclaimer page.",
    privacyLinkLabel: "Privacy Policy",
    termsLinkLabel: "Terms & Disclaimer",
    backToAbout: "Back to About",
    lastUpdatedLabel: "Last updated",
    footerPrivacy: "Privacy",
    footerTerms: "Terms",
    fallbackNotice: "This legal page is currently shown in English for the selected language."
  },
  "zh-CN": {
    sectionTitle: "法律与隐私",
    lead: "Pink Hunter 现已提供站点隐私政策，以及一份尽量用普通语言写成的使用条款与免责声明。",
    privacyLinkLabel: "隐私政策",
    termsLinkLabel: "条款与免责声明",
    backToAbout: "返回 About",
    lastUpdatedLabel: "最后更新",
    footerPrivacy: "隐私政策",
    footerTerms: "使用条款",
    fallbackNotice: "当前语言暂未提供完整译文，这个法律页面目前以英文显示。"
  },
  "zh-TW": {
    sectionTitle: "法律與隱私",
    lead: "Pink Hunter 現已提供站點隱私政策，以及一份盡量以白話文寫成的使用條款與免責聲明。",
    privacyLinkLabel: "隱私政策",
    termsLinkLabel: "條款與免責聲明",
    backToAbout: "返回 About",
    lastUpdatedLabel: "最後更新",
    footerPrivacy: "隱私政策",
    footerTerms: "使用條款",
    fallbackNotice: "目前這個語言尚未提供完整譯文，此法律頁面暫時以英文顯示。"
  }
};

const LEGAL_DOCUMENTS: Partial<Record<Language, Record<LegalDocumentId, LegalDocumentContent>>> = {
  "en-US": {
    privacy: {
      title: "Privacy Policy",
      summary:
        "This policy explains what Pink Hunter collects, what stays in your browser, what may be sent to service providers, and what choices you have when using the site.",
      lastUpdated: "March 10, 2026",
      sections: [
        {
          id: "scope",
          title: "1. Scope",
          paragraphs: [
            "This Privacy Policy applies to Pink Hunter at pinkhunter.flalaz.com and to closely related deployment environments that serve the same app.",
            "Pink Hunter is a public blossom-tree map and identification guide. It does not currently offer user accounts, payments, or user-uploaded content."
          ]
        },
        {
          id: "collect",
          title: "2. Information Pink Hunter collects",
          paragraphs: ["Pink Hunter collects or processes a limited set of information needed to run the map and measure aggregate site visits."],
          bullets: [
            "Basic request and device data that browsers normally send when loading a site, such as IP address, user agent, referrer, and request timestamps. These may be processed by the hosting stack and by third-party map or infrastructure providers.",
            "A random visitor identifier stored in your browser localStorage, plus a session marker stored in sessionStorage, for aggregate visitor counting. Pink Hunter does not create this visitor identifier when your browser sends a Do Not Track or Global Privacy Control signal.",
            "The page pathname associated with a visitor-count hit when Pink Hunter increments the aggregate site counter.",
            "Precise device location only if you choose the Locate feature. Pink Hunter uses those coordinates inside your browser session to center the map and find a nearby covered area."
          ]
        },
        {
          id: "use",
          title: "3. How Pink Hunter uses information",
          paragraphs: ["Pink Hunter uses the information above to operate and improve the site."],
          bullets: [
            "Load map tiles, styles, tree data, and related assets.",
            "Show an aggregate visitor count and prevent duplicate counting from the same browser profile during repeat visits.",
            "Center the map near you when you explicitly ask the site to use your location.",
            "Protect the service, investigate failures, and understand basic operational trends."
          ]
        },
        {
          id: "storage",
          title: "4. Cookies, local storage, and similar technologies",
          paragraphs: [
            "Pink Hunter does not currently use an account login cookie, ad-tech cookie, or marketing pixel.",
            "Pink Hunter does use browser localStorage and sessionStorage for visitor counting. If you clear browser storage, block storage, or browse in a more restricted mode, the visitor counter behavior may change or stop working."
          ]
        },
        {
          id: "sharing",
          title: "5. Third parties and disclosures",
          paragraphs: [
            "Pink Hunter relies on third-party infrastructure to deliver the site. Those providers may receive normal web request metadata when your browser asks them for assets or services."
          ],
          bullets: [
            "Site hosting and delivery infrastructure, including GitHub Pages and related CDN layers.",
            "Map and basemap providers, such as Carto, Mapbox, or comparable map-hosting services used by a given deployment environment.",
            "Visitor count infrastructure, which may be CounterAPI or a Pink Hunter AWS-backed counter endpoint depending on the deployment environment.",
            "Google Maps or Apple Maps if you choose the directions link for a tree."
          ]
        },
        {
          id: "retention",
          title: "6. Retention",
          paragraphs: [
            "The browser-side visitor identifier stays in localStorage until you clear it. The session marker stays in sessionStorage until the browser session ends or storage is cleared.",
            "Server-side visitor-counter records, aggregate counter values, and infrastructure logs may be retained for operational, security, and audit reasons until Pink Hunter deletes, rotates, or aggregates them."
          ]
        },
        {
          id: "choices",
          title: "7. Your choices",
          paragraphs: ["You have several practical controls when using Pink Hunter."],
          bullets: [
            "You can decline geolocation permission. The site will still work without it.",
            "You can clear or block browser storage. That may disable the persistent visitor identifier.",
            "If your browser sends Do Not Track or Global Privacy Control, Pink Hunter will not create the local visitor identifier and will not send a visitor-count increment request.",
            "You can contact flalaz@uw.edu with privacy questions or requests."
          ]
        },
        {
          id: "dnt",
          title: "8. Do Not Track and Global Privacy Control",
          paragraphs: [
            "As of March 10, 2026, Pink Hunter treats a browser Do Not Track signal or Global Privacy Control signal as a request not to create a persistent browser visitor identifier and not to increment the aggregate visitor counter.",
            "Pink Hunter does not promise that every third-party service on the internet will interpret those signals the same way."
          ]
        },
        {
          id: "changes",
          title: "9. Changes to this policy",
          paragraphs: [
            "Pink Hunter may update this Privacy Policy as the product changes. When that happens, the effective date at the top of the page will be updated."
          ]
        }
      ]
    },
    terms: {
      title: "Terms of Use and Data Disclaimer",
      summary:
        "These terms explain how Pink Hunter should be used, what the map is and is not promising, and what risks remain when using public tree-location data.",
      lastUpdated: "March 10, 2026",
      sections: [
        {
          id: "acceptance",
          title: "1. Use of the site",
          paragraphs: [
            "By using Pink Hunter, you agree to use the site only for lawful, informational, and personal or internal reference purposes.",
            "If you do not agree with these terms, do not use the site."
          ]
        },
        {
          id: "informational",
          title: "2. Informational service only",
          paragraphs: [
            "Pink Hunter is an informational map and species-identification aid. It is not legal advice, surveying advice, navigation advice, arborist advice, or a guarantee that a tree is present, blooming, accessible, safe, or correctly identified."
          ]
        },
        {
          id: "freshness",
          title: "3. Data accuracy, freshness, and limitations",
          paragraphs: [
            "Pink Hunter is built from public datasets and supporting research. Public datasets can lag reality, contain labeling errors, omit removals, or place tree points imprecisely."
          ],
          bullets: [
            "A tree on the map may no longer exist, may be on private property, or may not be reachable when you visit.",
            "A bloom window can shift because of weather, pruning, disease, construction, or normal seasonal variation.",
            "Coverage envelopes and research notes describe data coverage, not legal boundaries, ownership rights, or guaranteed public access."
          ]
        },
        {
          id: "conduct",
          title: "4. Respect property, safety, and local rules",
          paragraphs: ["You are responsible for your own conduct when using information from Pink Hunter."],
          bullets: [
            "Do not trespass or enter restricted property.",
            "Follow park rules, traffic laws, posted signs, and local access restrictions.",
            "Do not rely on Pink Hunter in emergencies or safety-critical situations."
          ]
        },
        {
          id: "third-party",
          title: "5. Third-party services and source data",
          paragraphs: [
            "Pink Hunter links to or depends on third-party services and public datasets. Those services and datasets have their own terms, privacy practices, licenses, and uptime characteristics.",
            "Pink Hunter does not control third-party websites or guarantee their continued availability."
          ]
        },
        {
          id: "ip",
          title: "6. Content and source rights",
          paragraphs: [
            "Pink Hunter’s interface, site copy, and original project materials remain subject to their applicable intellectual-property rights.",
            "Underlying public datasets, basemaps, and linked external materials remain subject to the terms and licenses set by their original providers."
          ]
        },
        {
          id: "liability",
          title: "7. No warranty; limitation of liability",
          paragraphs: [
            "Pink Hunter is provided on an “as is” and “as available” basis to the maximum extent permitted by law.",
            "To the maximum extent permitted by law, Pink Hunter and its operator are not liable for losses, injuries, property issues, access disputes, routing problems, or decisions you make based on the site."
          ]
        },
        {
          id: "changes",
          title: "8. Changes and contact",
          paragraphs: [
            "Pink Hunter may update these terms as the site changes. Questions about these terms can be sent to flalaz@uw.edu."
          ]
        }
      ]
    }
  },
  "zh-CN": {
    privacy: {
      title: "隐私政策",
      summary: "这份政策说明 Pink Hunter 会收集什么、什么信息只留在你的浏览器里、什么信息可能会发送给服务提供方，以及你有哪些控制选项。",
      lastUpdated: "2026年3月10日",
      sections: [
        {
          id: "scope",
          title: "1. 适用范围",
          paragraphs: [
            "本隐私政策适用于 pinkhunter.flalaz.com 上的 Pink Hunter，以及提供同一应用的相关部署环境。",
            "Pink Hunter 是一个公开的粉色花树地图与识别工具。目前没有用户账号、支付功能，也不提供用户上传内容。"
          ]
        },
        {
          id: "collect",
          title: "2. Pink Hunter 会处理哪些信息",
          paragraphs: ["Pink Hunter 只处理运行网站和统计整体访问量所需的一小部分信息。"],
          bullets: [
            "浏览器在访问网站时通常会发送的基础请求与设备信息，例如 IP 地址、浏览器标识、来源页和请求时间。这些信息可能由托管基础设施以及第三方地图或基础设施提供商处理。",
            "用于整体访客计数的随机访客标识符，会写入浏览器 localStorage；另有一个会话标记写入 sessionStorage。如果你的浏览器发送 Do Not Track 或 Global Privacy Control 信号，Pink Hunter 不会创建这个访客标识符。",
            "当 Pink Hunter 对站点总访问量进行计数递增时，会附带当前页面路径。",
            "只有当你主动使用“Locate/定位”功能时，Pink Hunter 才会读取精确设备位置。该坐标默认只在你的浏览器会话中使用，用来把地图移动到附近区域。"
          ]
        },
        {
          id: "use",
          title: "3. Pink Hunter 如何使用这些信息",
          paragraphs: ["Pink Hunter 使用上述信息来运行和改进网站。"],
          bullets: [
            "加载底图、样式、树木数据和相关资源。",
            "显示站点总访问量，并尽量避免同一浏览器资料在重复访问时被重复计数。",
            "在你主动授权时，把地图移动到你的附近区域。",
            "保障服务稳定性、排查故障，并理解基本运行趋势。"
          ]
        },
        {
          id: "storage",
          title: "4. Cookie、本地存储与类似技术",
          paragraphs: [
            "Pink Hunter 目前不使用登录 Cookie、广告追踪 Cookie，也不使用营销像素。",
            "Pink Hunter 会使用浏览器 localStorage 和 sessionStorage 来完成访客计数。如果你清除浏览器存储、阻止存储，或在更严格的浏览模式下访问，访客计数功能可能改变或停止工作。"
          ]
        },
        {
          id: "sharing",
          title: "5. 第三方服务与披露",
          paragraphs: ["Pink Hunter 依赖第三方基础设施提供网站服务。当你的浏览器向这些服务请求资源时，它们可能会收到正常的网页请求元数据。"],
          bullets: [
            "站点托管与分发基础设施，包括 GitHub Pages 及相关 CDN 层。",
            "地图与底图服务，例如 Carto、Mapbox，或某个部署环境中使用的类似地图托管服务。",
            "访客计数基础设施。根据部署环境不同，可能是 CounterAPI，也可能是 Pink Hunter 自有的 AWS 计数接口。",
            "如果你点击树点导航链接，Google Maps 或 Apple Maps 会接收相应坐标。"
          ]
        },
        {
          id: "retention",
          title: "6. 保留期限",
          paragraphs: [
            "浏览器端的访客标识符会保留在 localStorage 中，直到你主动清除。sessionStorage 中的会话标记会在浏览器会话结束或存储被清除后消失。",
            "服务端的访客计数记录、总计数值和基础设施日志，可能会因为运行、审计或安全原因而保留，直到 Pink Hunter 主动删除、轮换或聚合这些数据。"
          ]
        },
        {
          id: "choices",
          title: "7. 你的选择",
          paragraphs: ["你可以通过以下方式控制自己的使用方式。"],
          bullets: [
            "你可以拒绝地理位置授权，网站核心功能仍可使用。",
            "你可以清除或阻止浏览器存储，但这可能会禁用持久化访客标识。",
            "如果你的浏览器发送 Do Not Track 或 Global Privacy Control，Pink Hunter 不会创建本地访客标识，也不会发送访客计数递增请求。",
            "如有隐私相关问题，可以发邮件到 flalaz@uw.edu。"
          ]
        },
        {
          id: "dnt",
          title: "8. Do Not Track 与 Global Privacy Control",
          paragraphs: [
            "截至 2026 年 3 月 10 日，Pink Hunter 会把浏览器发出的 Do Not Track 或 Global Privacy Control 信号视为“不创建持久访客标识、也不增加总访客计数”的请求。",
            "但 Pink Hunter 无法承诺互联网上的每一个第三方服务都会以同样方式解释这些信号。"
          ]
        },
        {
          id: "changes",
          title: "9. 政策更新",
          paragraphs: ["如果产品发生变化，Pink Hunter 可能会更新本隐私政策。发生更新时，页面顶部的生效日期也会同步更新。"]
        }
      ]
    },
    terms: {
      title: "使用条款与数据免责声明",
      summary: "这份条款说明 Pink Hunter 应该如何使用、地图并不承诺什么，以及在使用公开树木数据时仍然存在的风险。",
      lastUpdated: "2026年3月10日",
      sections: [
        {
          id: "acceptance",
          title: "1. 网站使用",
          paragraphs: [
            "使用 Pink Hunter 即表示你同意仅将本网站用于合法、信息参考以及个人或内部参考用途。",
            "如果你不同意这些条款，请不要使用本网站。"
          ]
        },
        {
          id: "informational",
          title: "2. 仅供信息参考",
          paragraphs: [
            "Pink Hunter 是一个信息查询地图和花树识别辅助工具。它不是法律意见、测绘意见、导航意见、树艺意见，也不保证某棵树一定存在、一定正在开花、一定可达、一定安全，或一定被正确识别。"
          ]
        },
        {
          id: "freshness",
          title: "3. 数据准确性、时效性与局限",
          paragraphs: ["Pink Hunter 基于公开数据集和补充研究构建。公开数据与现实之间可能存在时间差，也可能包含标注错误、遗漏已移除树木，或坐标不精确。"],
          bullets: [
            "地图上的树木可能已经不存在、位于私人土地上，或者在你到达时并不可进入。",
            "花期会受到天气、修剪、病害、施工和自然季节变化影响。",
            "Coverage Envelope 和研究说明只表达数据覆盖范围，不代表法律边界、产权归属或保证公众可进入。"
          ]
        },
        {
          id: "conduct",
          title: "4. 请尊重产权、安全和当地规则",
          paragraphs: ["你需要对自己如何使用 Pink Hunter 上的信息负责。"],
          bullets: [
            "不要擅自进入私人或限制区域。",
            "请遵守公园规则、交通法规、现场标识和当地访问限制。",
            "不要在紧急情况或安全关键情形下依赖 Pink Hunter。"
          ]
        },
        {
          id: "third-party",
          title: "5. 第三方服务与源数据",
          paragraphs: [
            "Pink Hunter 会链接到或依赖第三方服务和公开数据集。这些服务和数据集各自有自己的条款、隐私政策、许可证和可用性情况。",
            "Pink Hunter 不控制第三方网站，也不保证它们会持续可用。"
          ]
        },
        {
          id: "ip",
          title: "6. 内容与来源权利",
          paragraphs: [
            "Pink Hunter 的界面、站点文案和项目原创材料受各自适用的知识产权规则保护。",
            "底层公开数据、底图和外部链接内容仍受其原始提供方的条款与许可约束。"
          ]
        },
        {
          id: "liability",
          title: "7. 不作保证；责任限制",
          paragraphs: [
            "在法律允许的最大范围内，Pink Hunter 按“现状”和“可获得”方式提供。",
            "在法律允许的最大范围内，Pink Hunter 及其运营者不对你基于本网站作出的路线、访问、产权、拍摄、安全或其他决定所造成的损失、争议或伤害承担责任。"
          ]
        },
        {
          id: "changes",
          title: "8. 条款更新与联系",
          paragraphs: ["如果网站发生变化，Pink Hunter 可能会更新这些条款。如有问题，请发邮件到 flalaz@uw.edu。"]
        }
      ]
    }
  },
  "zh-TW": {
    privacy: {
      title: "隱私政策",
      summary: "這份政策說明 Pink Hunter 會蒐集什麼、哪些資訊只留在你的瀏覽器中、哪些資訊可能會傳送給服務提供方，以及你有哪些控制選項。",
      lastUpdated: "2026年3月10日",
      sections: [
        {
          id: "scope",
          title: "1. 適用範圍",
          paragraphs: [
            "本隱私政策適用於 pinkhunter.flalaz.com 上的 Pink Hunter，以及提供同一應用的相關部署環境。",
            "Pink Hunter 是一個公開的粉色花樹地圖與辨識工具。目前沒有使用者帳號、支付功能，也不提供使用者上傳內容。"
          ]
        },
        {
          id: "collect",
          title: "2. Pink Hunter 會處理哪些資訊",
          paragraphs: ["Pink Hunter 只處理執行網站和統計整體訪問量所需的一小部分資訊。"],
          bullets: [
            "瀏覽器在造訪網站時通常會送出的基礎請求與裝置資訊，例如 IP 位址、瀏覽器標識、來源頁與請求時間。這些資訊可能由託管基礎設施以及第三方地圖或基礎設施提供商處理。",
            "用於整體訪客計數的隨機訪客識別符，會寫入瀏覽器 localStorage；另有一個工作階段標記寫入 sessionStorage。如果你的瀏覽器送出 Do Not Track 或 Global Privacy Control 訊號，Pink Hunter 不會建立這個訪客識別符。",
            "當 Pink Hunter 對站點總訪問量進行計數遞增時，會附帶目前頁面路徑。",
            "只有當你主動使用「Locate/定位」功能時，Pink Hunter 才會讀取精確裝置位置。該座標預設只在你的瀏覽器工作階段內使用，用來把地圖移動到附近區域。"
          ]
        },
        {
          id: "use",
          title: "3. Pink Hunter 如何使用這些資訊",
          paragraphs: ["Pink Hunter 使用上述資訊來執行與改進網站。"],
          bullets: [
            "載入底圖、樣式、樹木資料與相關資源。",
            "顯示站點總訪問量，並盡量避免同一瀏覽器設定檔在重複造訪時被重複計數。",
            "在你主動授權時，把地圖移動到你的附近區域。",
            "保障服務穩定性、排查故障，並理解基本運行趨勢。"
          ]
        },
        {
          id: "storage",
          title: "4. Cookie、本地儲存與類似技術",
          paragraphs: [
            "Pink Hunter 目前不使用登入 Cookie、廣告追蹤 Cookie，也不使用行銷像素。",
            "Pink Hunter 會使用瀏覽器 localStorage 與 sessionStorage 來完成訪客計數。如果你清除瀏覽器儲存、阻止儲存，或在更嚴格的瀏覽模式下造訪，訪客計數功能可能改變或停止運作。"
          ]
        },
        {
          id: "sharing",
          title: "5. 第三方服務與揭露",
          paragraphs: ["Pink Hunter 依賴第三方基礎設施提供網站服務。當你的瀏覽器向這些服務請求資源時，它們可能會收到一般的網頁請求中繼資料。"],
          bullets: [
            "站點託管與分發基礎設施，包括 GitHub Pages 與相關 CDN 層。",
            "地圖與底圖服務，例如 Carto、Mapbox，或某個部署環境中使用的類似地圖託管服務。",
            "訪客計數基礎設施。依部署環境不同，可能是 CounterAPI，也可能是 Pink Hunter 自有的 AWS 計數介面。",
            "如果你點擊樹點導航連結，Google Maps 或 Apple Maps 會接收相應座標。"
          ]
        },
        {
          id: "retention",
          title: "6. 保留期限",
          paragraphs: [
            "瀏覽器端的訪客識別符會保留在 localStorage 中，直到你主動清除。sessionStorage 中的工作階段標記會在瀏覽器工作階段結束或儲存被清除後消失。",
            "伺服器端的訪客計數紀錄、總計數值和基礎設施日誌，可能會因為運作、稽核或安全原因而保留，直到 Pink Hunter 主動刪除、輪替或彙總這些資料。"
          ]
        },
        {
          id: "choices",
          title: "7. 你的選擇",
          paragraphs: ["你可以透過以下方式控制自己的使用方式。"],
          bullets: [
            "你可以拒絕地理位置授權，網站核心功能仍可使用。",
            "你可以清除或阻止瀏覽器儲存，但這可能會停用持久化訪客識別符。",
            "如果你的瀏覽器送出 Do Not Track 或 Global Privacy Control，Pink Hunter 不會建立本地訪客識別符，也不會送出訪客計數遞增請求。",
            "如有隱私相關問題，可以寄信到 flalaz@uw.edu。"
          ]
        },
        {
          id: "dnt",
          title: "8. Do Not Track 與 Global Privacy Control",
          paragraphs: [
            "截至 2026 年 3 月 10 日，Pink Hunter 會把瀏覽器送出的 Do Not Track 或 Global Privacy Control 訊號視為「不建立持久訪客識別符、也不增加總訪客計數」的請求。",
            "但 Pink Hunter 無法承諾網際網路上的每一個第三方服務都會以同樣方式解讀這些訊號。"
          ]
        },
        {
          id: "changes",
          title: "9. 政策更新",
          paragraphs: ["如果產品發生變化，Pink Hunter 可能會更新本隱私政策。發生更新時，頁面頂部的生效日期也會同步更新。"]
        }
      ]
    },
    terms: {
      title: "使用條款與資料免責聲明",
      summary: "這份條款說明 Pink Hunter 應該如何使用、地圖並不承諾什麼，以及在使用公開樹木資料時仍然存在的風險。",
      lastUpdated: "2026年3月10日",
      sections: [
        {
          id: "acceptance",
          title: "1. 網站使用",
          paragraphs: [
            "使用 Pink Hunter 即表示你同意僅將本網站用於合法、資訊參考以及個人或內部參考用途。",
            "如果你不同意這些條款，請不要使用本網站。"
          ]
        },
        {
          id: "informational",
          title: "2. 僅供資訊參考",
          paragraphs: [
            "Pink Hunter 是一個資訊查詢地圖和花樹辨識輔助工具。它不是法律意見、測繪意見、導航意見、樹藝意見，也不保證某棵樹一定存在、一定正在開花、一定可達、一定安全，或一定被正確辨識。"
          ]
        },
        {
          id: "freshness",
          title: "3. 資料準確性、時效性與限制",
          paragraphs: ["Pink Hunter 依據公開資料集與補充研究建立。公開資料與現實之間可能存在時間差，也可能包含標註錯誤、遺漏已移除樹木，或座標不精確。"],
          bullets: [
            "地圖上的樹木可能已經不存在、位於私人土地上，或在你到達時並不可進入。",
            "花期會受到天氣、修剪、病害、施工與自然季節變化影響。",
            "Coverage Envelope 與研究說明只表達資料覆蓋範圍，不代表法律邊界、產權歸屬或保證公眾可進入。"
          ]
        },
        {
          id: "conduct",
          title: "4. 請尊重產權、安全與當地規則",
          paragraphs: ["你需要對自己如何使用 Pink Hunter 上的資訊負責。"],
          bullets: [
            "不要擅自進入私人或限制區域。",
            "請遵守公園規則、交通法規、現場標示與當地訪問限制。",
            "不要在緊急情況或安全關鍵情境下依賴 Pink Hunter。"
          ]
        },
        {
          id: "third-party",
          title: "5. 第三方服務與來源資料",
          paragraphs: [
            "Pink Hunter 會連結到或依賴第三方服務與公開資料集。這些服務與資料集各自有自己的條款、隱私政策、授權與可用性情況。",
            "Pink Hunter 不控制第三方網站，也不保證它們會持續可用。"
          ]
        },
        {
          id: "ip",
          title: "6. 內容與來源權利",
          paragraphs: [
            "Pink Hunter 的介面、站點文案與專案原創材料受各自適用的智慧財產權規則保護。",
            "底層公開資料、底圖與外部連結內容仍受其原始提供方的條款與授權約束。"
          ]
        },
        {
          id: "liability",
          title: "7. 不作保證；責任限制",
          paragraphs: [
            "在法律允許的最大範圍內，Pink Hunter 以「現狀」與「可取得」方式提供。",
            "在法律允許的最大範圍內，Pink Hunter 及其營運者不對你基於本網站作出的路線、訪問、產權、拍攝、安全或其他決定所造成的損失、爭議或傷害承擔責任。"
          ]
        },
        {
          id: "changes",
          title: "8. 條款更新與聯絡",
          paragraphs: ["如果網站發生變化，Pink Hunter 可能會更新這些條款。如有問題，請寄信到 flalaz@uw.edu。"]
        }
      ]
    }
  }
};

export function getLegalUiCopy(language: Language): LegalUiCopy {
  return LEGAL_UI_COPY[language] ?? LEGAL_UI_COPY["en-US"]!;
}

export function getLegalDocument(
  language: Language,
  documentId: LegalDocumentId
): {
  content: LegalDocumentContent;
  fallbackLanguage: Language | null;
} {
  const localized = LEGAL_DOCUMENTS[language];
  if (localized) {
    return {
      content: localized[documentId],
      fallbackLanguage: null
    };
  }

  return {
    content: LEGAL_DOCUMENTS["en-US"]![documentId],
    fallbackLanguage: "en-US"
  };
}
