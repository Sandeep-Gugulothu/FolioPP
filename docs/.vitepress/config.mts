import { defineConfig } from 'vitepress'

export default defineConfig({
    title: "FolioPP",
    description: "Institutional Full-Stack Trading Terminal Documentation",
    head: [
        ['link', { rel: 'icon', href: '/FolioPP.png' }]
    ],
    themeConfig: {
        logo: '/FolioPP.png',
        siteTitle: 'FolioPP',
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Problem', link: '/problem' },
            { text: 'Solution', link: '/solution' },
            { text: 'Credits', link: '/credits' }
        ],
        sidebar: [
            {
                text: 'Introduction',
                items: [
                    { text: 'The Problem', link: '/problem' },
                    { text: 'The Solution', link: '/solution' }
                ]
            },
            {
                text: 'About',
                items: [
                    { text: 'Credits', link: '/credits' }
                ]
            }
        ],
        socialLinks: [
            { icon: 'github', link: 'https://github.com/Sandeep-Gugulothu/FolioPP' }
        ]
    }
})
