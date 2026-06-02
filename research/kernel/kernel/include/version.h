/*
 * kernel/include/version.h — ArizenOS Version Definitions
 *
 * Single source of truth for the kernel version.
 * Updated during the release process — see docs/playbooks/release-playbook.md
 *
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 ArizenOS Contributors
 */

#ifndef KERNEL_VERSION_H
#define KERNEL_VERSION_H

#define ARIZENOS_VERSION_MAJOR  0
#define ARIZENOS_VERSION_MINOR  1
#define ARIZENOS_VERSION_PATCH  0
#define ARIZENOS_VERSION_PRE    "dev"       /* Empty string for stable releases */

/* Helpers for numeric comparisons */
#define ARIZENOS_VERSION_NUM(major, minor, patch) \
    ((major) * 10000 + (minor) * 100 + (patch))

#define ARIZENOS_VERSION_CODE \
    ARIZENOS_VERSION_NUM(ARIZENOS_VERSION_MAJOR, ARIZENOS_VERSION_MINOR, ARIZENOS_VERSION_PATCH)

/* Human-readable version string */
#ifdef ARIZENOS_VERSION_PRE
  #define ARIZENOS_VERSION \
    "v" #ARIZENOS_VERSION_MAJOR "." #ARIZENOS_VERSION_MINOR "." #ARIZENOS_VERSION_PATCH "-" ARIZENOS_VERSION_PRE
#else
  #define ARIZENOS_VERSION \
    "v" #ARIZENOS_VERSION_MAJOR "." #ARIZENOS_VERSION_MINOR "." #ARIZENOS_VERSION_PATCH
#endif

/* Build timestamp — injected by the build system */
#ifndef ARIZENOS_BUILD_DATE
  #define ARIZENOS_BUILD_DATE __DATE__
#endif

#ifndef ARIZENOS_BUILD_TIME
  #define ARIZENOS_BUILD_TIME __TIME__
#endif

#endif /* KERNEL_VERSION_H */
