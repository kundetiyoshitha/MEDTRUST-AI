document.addEventListener("DOMContentLoaded", () => {

    const sidebarLinks =
        document.querySelectorAll(".sidebar a[href]");

    /*
     * History is a separate page.
     * Remove the old embedded History section from
     * the main dashboard so users don't see it twice.
     */
    const dashboardHistorySection =
        document.getElementById("history-section");

    if (dashboardHistorySection) {
        dashboardHistorySection.remove();
    }


    // =========================================================
    // SIDEBAR NAVIGATION
    // =========================================================

    sidebarLinks.forEach(link => {

        link.addEventListener("click", event => {

            const href =
                link.getAttribute("href") || "";

            // Dashboard home
            if (href === "/user-dashboard") {

                event.preventDefault();

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

                setActiveLink(link);

                history.replaceState(
                    null,
                    "",
                    "/user-dashboard"
                );

                return;
            }


            /*
             * Same-page dashboard sections.
             *
             * Example:
             * /user-dashboard#analyzer-section
             */
            if (
                href.startsWith(
                    "/user-dashboard#"
                )
            ) {

                const hash =
                    href.split("#")[1];

                const section =
                    document.getElementById(hash);

                if (section) {

                    event.preventDefault();

                    section.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                    setActiveLink(link);

                    history.replaceState(
                        null,
                        "",
                        `#${hash}`
                    );

                }

                return;
            }


            /*
             * History is a real route.
             * Let the browser navigate normally.
             */
            if (href === "/history") {
                return;
            }


            /*
             * Logout/access links also navigate normally.
             */
            if (
                href === "/access" ||
                href === "/" ||
                href === "/logout"
            ) {
                return;
            }

        });

    });


    // =========================================================
    // ACTIVE SIDEBAR STATE WHILE SCROLLING
    // =========================================================

    const sections = [
        document.getElementById("analyzer-section"),
        document.getElementById("evidence-section"),
        document.getElementById("learning-section"),
        document.getElementById("settings-section")
    ].filter(Boolean);


    if (
        "IntersectionObserver" in window &&
        sections.length > 0
    ) {

        const observer =
            new IntersectionObserver(
                entries => {

                    const visibleEntries =
                        entries.filter(
                            entry =>
                                entry.isIntersecting
                        );

                    if (!visibleEntries.length) {
                        return;
                    }

                    /*
                     * Choose the section with the
                     * highest visible percentage.
                     */
                    visibleEntries.sort(
                        (a, b) =>
                            b.intersectionRatio -
                            a.intersectionRatio
                    );

                    const activeSection =
                        visibleEntries[0];

                    const id =
                        activeSection.target.id;

                    sidebarLinks.forEach(link => {

                        const href =
                            link.getAttribute(
                                "href"
                            ) || "";

                        link.classList.toggle(
                            "active",
                            href.includes(
                                `#${id}`
                            )
                        );

                    });

                },
                {
                    root: null,
                    threshold: [
                        0.15,
                        0.30,
                        0.50,
                        0.70
                    ],
                    rootMargin:
                        "-10% 0px -60% 0px"
                }
            );


        sections.forEach(section => {
            observer.observe(section);
        });
    }


    // =========================================================
    // DASHBOARD LOGO
    // =========================================================

    const logo =
        document.querySelector(
            ".sidebar-logo"
        );

    if (logo) {

        logo.addEventListener(
            "click",
            event => {

                const href =
                    logo.getAttribute(
                        "href"
                    );

                if (
                    href ===
                    "/user-dashboard"
                ) {

                    event.preventDefault();

                    window.scrollTo({
                        top: 0,
                        behavior: "smooth"
                    });

                    history.replaceState(
                        null,
                        "",
                        "/user-dashboard"
                    );

                    const dashboardLink =
                        document.querySelector(
                            '.sidebar a[href="/user-dashboard"]'
                        );

                    if (dashboardLink) {
                        setActiveLink(
                            dashboardLink
                        );
                    }
                }

            }
        );

    }


    // =========================================================
    // LOGOUT CLEANUP
    // =========================================================

    const logoutLinks =
        document.querySelectorAll(
            'a[href="/access"], a[href="/logout"], .logout-button'
        );

    logoutLinks.forEach(link => {

        link.addEventListener(
            "click",
            () => {

                sessionStorage.removeItem(
                    "medtrust_user"
                );

            }
        );

    });


    // =========================================================
    // RESTORE HASH ON PAGE LOAD
    // =========================================================

    if (window.location.hash) {

        const sectionId =
            window.location.hash.substring(1);

        const section =
            document.getElementById(
                sectionId
            );

        if (section) {

            setTimeout(() => {

                section.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }, 200);

        }

    }


    // =========================================================
    // HELPER
    // =========================================================

    function setActiveLink(activeLink) {

        sidebarLinks.forEach(link => {
            link.classList.remove("active");
        });

        activeLink.classList.add("active");
    }


    console.log(
        "MEDTRUST AI dashboard.js loaded successfully."
    );

});