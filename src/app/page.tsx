"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  detectLanguage,
  getTranslations,
  Translations,
} from "@/utils/translations";

export default function Home() {
  const [lang, setLang] = useState("en");
  const [translations, setTranslations] = useState<Translations>(
    {} as Translations,
  );

  useEffect(() => {
    const detectedLang = detectLanguage();
    setLang(detectedLang);
    setTranslations(getTranslations(detectedLang));
  }, []);

  if (!translations.welcome) return null;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-8">{translations.welcome}</h1>
      <Link
        href={`/chat?lang=${lang}`}
        className="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        {translations.getStarted}
      </Link>
    </div>
  );
}
