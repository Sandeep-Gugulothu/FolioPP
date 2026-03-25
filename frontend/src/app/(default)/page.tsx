export const metadata = {
  title: "Home - FolioPP",
  description: "Page description",
};

import Hero from "@/components/v1-landing/hero-home";
import BusinessCategories from "@/components/v1-landing/business-categories";
import FeaturesPlanet from "@/components/v1-landing/features-planet";
import LargeTestimonial from "@/components/v1-landing/large-testimonial";
import Cta from "@/components/v1-landing/cta";

export default function Home() {
  return (
    <>
      <Hero />
      <BusinessCategories />
      <FeaturesPlanet />
      <LargeTestimonial />
      <Cta />
    </>
  );
}
