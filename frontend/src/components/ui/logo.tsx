import Image from "next/image";
import LogoImage from "@/public/images/logo-foliopp.png";

export default function Logo() {
  return (
    <a href="/" className="inline-flex items-center gap-2" aria-label="FolioPP">
      <Image
        src={LogoImage}
        alt="FolioPP Logo"
        width={32}
        height={32}
        priority
        className="rounded-lg"
      />
      <span className="text-xl font-bold tracking-tight text-gray-900">
        Folio<span className="text-blue-600">PP</span>
      </span>
    </a>
  );
}
