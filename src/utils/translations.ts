import en from "@/locales/en.json";
import pt from "@/locales/pt.json";

const translations = { en, pt };

export interface Translations {
  welcome: string;
  getStarted: string;
  typeMessage: string;
  send: string;
  chatTitle: string;
  [key: string]: string;
}

export function getTranslations(lang: string): Translations {
  return (translations[lang as keyof typeof translations] ||
    translations.en) as Translations;
}

export function detectLanguage(): string {
  if (typeof window !== "undefined") {
    const browserLang = navigator.language.split("-")[0];
    return ["pt", "en"].includes(browserLang) ? browserLang : "en";
  }
  return "en";
}
