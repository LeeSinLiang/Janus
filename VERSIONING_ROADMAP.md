# Campaign Versioning Roadmap

This document outlines future enhancements for the campaign versioning system.

## Current Implementation (v1.0)

### ✅ Completed Features

- **Phase-based Regeneration**: `!regenerate phase X` command to regenerate from specific phase
- **Version Tracking**: `Campaign.current_version` and `Post.version` fields
- **Soft Delete**: `Post.is_active` flag for archiving old posts
- **Many-to-Many Connections**: Support for branching (1→N) and merging (N→1) patterns
- **Smart Linking**: Strategy planner determines connections between old and new posts
- **Dynamic Node Count**: 2-5 nodes per phase (not fixed at 3)
- **Background Content Generation**: Automatic A/B content and media generation for new posts

### Database Schema

```python
class Campaign(models.Model):
    campaign_id = CharField(max_length=255, unique=True)
    current_version = IntegerField(default=1)  # ✅ NEW
    strategy = TextField()  # Mermaid diagram
    # ... other fields

class Post(models.Model):
    post_id = CharField(max_length=255)
    campaign = ForeignKey(Campaign)
    version = IntegerField(default=1)  # ✅ NEW
    is_active = BooleanField(default=True)  # ✅ NEW
    next_posts = ManyToManyField('self')
    # ... other fields
```

### API Endpoints

- `POST /api/agents/regenerate-strategy/` - Regenerate campaign from specific phase

### Frontend Components

- `ChatBox.tsx` - Detects `!regenerate phase X` command
- `api.ts` - `regenerateStrategy()` API client method

---

## Future Enhancements

### Phase 1: Version History UI (Q2 2025)

**Goal:** Allow users to view and compare different versions of their campaign strategy.

#### Features

1. **Version Selector Dropdown**
   - Location: Canvas page header
   - Shows list of all versions with timestamps
   - Quick switch between versions for comparison

2. **Version Timeline View**
   - Visual timeline showing all strategy iterations
   - Display version number, timestamp, and change description
   - Click to view that version's campaign graph

3. **Version Metadata**
   - Add `Campaign.version_history` JSONField:
     ```json
     [
       {
         "version": 1,
         "created_at": "2025-01-15T10:00:00Z",
         "created_by": "user_123",
         "description": "Initial strategy",
         "phase_regenerated": null
       },
       {
         "version": 2,
         "created_at": "2025-01-20T14:30:00Z",
         "created_by": "user_123",
         "description": "Regenerated from Phase 2",
         "phase_regenerated": 2,
         "prompt": "Focus on developer communities"
       }
     ]
     ```

4. **Read-Only Version View**
   - Display archived posts when viewing old versions
   - Grayed out UI to indicate read-only mode
   - "Restore This Version" button to reactivate

#### Technical Implementation

- Add `GET /api/agents/campaigns/{id}/versions/` endpoint
- Filter posts by `version` field
- Update `useGraphData` hook to accept version parameter
- Add version selector component in canvas header

---

### Phase 2: Version Comparison (Q3 2025)

**Goal:** Side-by-side comparison of different campaign versions.

#### Features

1. **Split-Screen Canvas View**
   - Show two versions side-by-side
   - Highlight differences (added/removed/modified nodes)
   - Color coding:
     - Green: Added nodes
     - Red: Removed nodes
     - Yellow: Modified nodes

2. **Diff Summary Panel**
   - List all changes between versions
   - Show post title, phase, and change type
   - Click to focus on specific change in canvas

3. **Metrics Comparison**
   - Compare performance metrics across versions
   - Show which version performed better
   - Highlight winning A/B variants

#### Technical Implementation

- Add `GET /api/agents/campaigns/{id}/compare/?v1=1&v2=2` endpoint
- Create `VersionComparisonView` component
- Implement diff algorithm for Mermaid diagrams
- Add metrics aggregation by version

---

### Phase 3: Version Restoration (Q4 2025)

**Goal:** Restore previous campaign versions and merge strategies.

#### Features

1. **One-Click Restoration**
   - "Restore Version X" button in version history
   - Archives current active posts
   - Reactivates posts from selected version
   - Increments version number

2. **Selective Restoration**
   - Restore only specific phases from old version
   - Example: Keep current Phase 1, restore old Phase 2
   - Merge strategy from multiple versions

3. **Restoration Confirmation Dialog**
   - Show what will change
   - Warn about losing current active posts
   - Require user confirmation

4. **Undo/Redo Stack**
   - Keep last 10 actions in memory
   - Quick undo regeneration if mistake made
   - Session-based (doesn't persist across reloads)

#### Technical Implementation

- Add `POST /api/agents/campaigns/{id}/restore/` endpoint
- Implement transaction-based restoration
- Add `Campaign.restoration_history` JSONField
- Create confirmation modal component

---

### Phase 4: Branching Strategies (2026)

**Goal:** Create multiple strategy branches for experimentation.

#### Features

1. **Strategy Branches**
   - Fork campaign into multiple branches
   - Example: "ProductHunt Launch" vs "Twitter Launch"
   - Independent development and testing

2. **Branch Comparison**
   - Compare metrics across branches
   - A/B test entire strategies
   - Merge winning branch back to main

3. **Branch Metadata**
   ```python
   class CampaignBranch(models.Model):
       branch_id = CharField(max_length=255, unique=True)
       campaign = ForeignKey(Campaign)
       name = CharField(max_length=255)  # e.g., "ProductHunt-focused"
       parent_branch = ForeignKey('self', null=True)
       is_main = BooleanField(default=False)
       created_at = DateTimeField()
   ```

4. **Branch Visualization**
   - Git-like branch graph
   - Show divergence points
   - Visual merge flow

#### Technical Implementation

- Major schema refactor: Posts linked to branches
- Add branching endpoints
- Create branch management UI
- Implement merge conflict resolution

---

### Phase 5: Collaborative Versioning (2026)

**Goal:** Multiple users can collaborate on campaign strategies.

#### Features

1. **User Tracking**
   - Track who created each version
   - Show user avatars in version history
   - Filter versions by user

2. **Version Comments**
   - Add notes to each version
   - Explain why regeneration happened
   - Team discussion thread

3. **Version Approval Workflow**
   - Require approval before activating new version
   - Assign reviewers
   - Approval status badges

4. **Conflict Resolution**
   - Detect concurrent edits
   - Merge strategies from multiple users
   - Conflict resolution UI

#### Technical Implementation

- Add user authentication system
- Create approval workflow models
- Implement WebSocket for real-time updates
- Add commenting system

---

## Technical Considerations

### Database Performance

- **Current**: SQLite (development)
- **Production**: Migrate to PostgreSQL
- **Indexing**: Add indexes on `version`, `is_active`, `campaign + version`
- **Archival**: Archive old versions to cold storage after 6 months

### Storage Optimization

- Compress archived Mermaid diagrams
- Store diffs instead of full diagrams for versions
- Implement cleanup job for orphaned ContentVariants

### API Rate Limiting

- Limit regenerations to 10 per hour per campaign
- Cache version history for 5 minutes
- Implement pagination for version lists

### Frontend Performance

- Lazy load version history (load on demand)
- Virtual scrolling for long version lists
- Cache rendered Mermaid diagrams

---

## Migration Path

### From v1.0 to v2.0 (Version History UI)

1. Add `Campaign.version_history` JSONField (migration)
2. Backfill version_history for existing campaigns
3. Deploy new frontend components
4. Update documentation

### From v2.0 to v3.0 (Branching)

1. Create `CampaignBranch` model
2. Migrate existing posts to "main" branch
3. Add branching UI
4. Train users on branching concepts

---

## User Feedback Integration

### Metrics to Track

- Regeneration frequency per campaign
- Most commonly regenerated phases
- Version restoration rate
- Average versions per campaign
- User engagement with version history

### Survey Questions

- How often do you need to regenerate strategies?
- What phases do you regenerate most?
- Would you use version comparison?
- Do you need collaborative features?

---

## Configuration Options (Future)

### Campaign Settings

```python
class CampaignSettings(models.Model):
    campaign = ForeignKey(Campaign)
    max_versions = IntegerField(default=10)  # Keep last 10 versions
    auto_archive_after_days = IntegerField(default=30)
    require_approval = BooleanField(default=False)
    enable_branching = BooleanField(default=False)
```

---

## Documentation TODO

- [ ] Create video tutorial for version management
- [ ] Add version management section to user guide
- [ ] Document API endpoints in OpenAPI spec
- [ ] Create troubleshooting guide for version conflicts
- [ ] Add examples to CLAUDE.md

---

## Related Documents

- `CLAUDE.md` - Main project documentation
- `backend/STRATEGY_REGENERATION.md` - Regeneration feature guide (created by agent)
- `backend/API_REGENERATION.md` - API reference (created by agent)
- `frontend/janus/APPROVAL_SYSTEM.md` - Node approval flow
- `AB_METRICS_MIGRATION_PLAN.md` - A/B metrics architecture

---

## Questions for Product Team

1. Should we implement automatic version cleanup? If yes, after how many versions?
2. Do we need real-time collaboration (WebSocket) or is polling sufficient?
3. What's the priority: Comparison UI or Restoration features?
4. Should branching be available to all users or enterprise only?
5. Do we need export/import functionality for campaign versions?
6. Should we integrate with version control systems (Git)?
7. What's the expected number of versions per campaign (10? 50? 100?)?

---

**Last Updated:** 2025-01-15
**Status:** Draft
**Owner:** Product & Engineering Team
