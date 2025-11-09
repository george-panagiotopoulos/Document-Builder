# Content Intake Service - Web UI

A modern web interface for the Content Intake Service, providing a user-friendly way to create and manage document intake sessions.

## Features

### 1. Home Page (`/`)
- Overview of the service
- Quick access to key features
- System status information
- API documentation links

### 2. New Session (`/sessions/new`)
- **Design Intent Configuration**:
  - Purpose selection (Report, Presentation, Proposal, Playbook)
  - Audience targeting (Technical, Executive, Customer, Internal)
  - Tone selection (Formal, Conversational, Persuasive, Educational)
  - Visual density control (Tight, Balanced, Airy)

- **Content Block Management**:
  - Add multiple content blocks (Heading, Paragraph, List, Quote, Callout)
  - Specify heading levels (0-6)
  - Live preview of added blocks
  - Remove/reorder functionality

- **Image Asset Management**:
  - Add images with URI, alt text, and format
  - Support for PNG, JPG, JPEG, SVG
  - Visual preview of added images

- **Validation**:
  - Client-side validation before submission
  - Required field checking
  - Format validation

### 3. Session Detail (`/sessions/{id}`)
- Real-time session status display
- Session information card
- Submit for layout generation
- Artifacts listing
- Status badges with color coding

### 4. Dashboard (`/dashboard`)
- Session statistics
- Recent sessions list (placeholder for future implementation)
- Quick actions

## Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Vanilla JS for interactivity
- **No framework dependencies**: Lightweight and fast

### Backend Integration
- **FastAPI**: Serves static files and templates
- **Jinja2**: Template rendering
- **REST API**: Full integration with backend endpoints

## UI Components

### Styling Features
- **Responsive Design**: Mobile-first approach
- **Color Scheme**: Professional blue theme with semantic colors
- **Typography**: System fonts for optimal performance
- **Status Badges**: Color-coded status indicators
- **Loading States**: Spinner for async operations
- **Alerts**: Success, error, and info messages

### JavaScript Features
- **Async/Await**: Modern promise handling
- **Fetch API**: RESTful API integration
- **DOM Manipulation**: Dynamic content updates
- **Form Validation**: Client-side validation
- **Error Handling**: Graceful error display

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Service

```bash
uvicorn services.content_intake.main:app --reload --port 8001
```

### 3. Access the UI

Open your browser to:
- **Home**: http://localhost:8001/
- **New Session**: http://localhost:8001/sessions/new
- **API Docs**: http://localhost:8001/docs

## Usage Guide

### Creating a Session

1. Navigate to `/sessions/new`
2. Configure design intent (purpose, audience, tone, density)
3. Add content blocks:
   - Select block type
   - Enter content text
   - Set level (for headings)
   - Click "Add Content Block"
4. Optionally add images:
   - Enter image URI
   - Provide alt text for accessibility
   - Select format
   - Click "Add Image"
5. Review added content in the preview
6. Click "Create Session"
7. Redirected to session detail page

### Viewing Session Details

1. Navigate to `/sessions/{session_id}` or click on a session
2. View session metadata and status
3. Submit for layout generation when ready
4. Check artifacts as they become available

## API Integration

The UI makes the following API calls:

```javascript
// Create session
POST /v1/intake/sessions
Content-Type: application/json
Body: { content_blocks, images, design_intent, constraints }

// Get session
GET /v1/intake/sessions/{session_id}

// Submit session
POST /v1/intake/sessions/{session_id}/submit
Body: { layout_mode: "rule_only" }

// Get artifacts
GET /v1/intake/sessions/{session_id}/artifacts
```

## File Structure

```
services/content_intake/ui/
├── __init__.py
├── routes.py                 # FastAPI route handlers
├── static/
│   ├── style.css            # Styles
│   └── app.js               # JavaScript logic
└── templates/
    ├── base.html            # Base template
    ├── index.html           # Home page
    ├── new_session.html     # Session creation form
    ├── session_detail.html  # Session detail view
    └── dashboard.html       # Dashboard
```

## Customization

### Styling

Edit `static/style.css` to customize:
- Color scheme (`:root` variables)
- Typography
- Layout and spacing
- Component styles

### Templates

Modify HTML templates in `templates/` directory:
- `base.html`: Site-wide layout and navigation
- Individual pages: Page-specific content

### JavaScript

Update `static/app.js` to:
- Add new features
- Modify API integration
- Enhance form validation
- Add animations

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

- **ARIA Labels**: Proper labeling for screen readers
- **Keyboard Navigation**: Full keyboard support
- **Color Contrast**: WCAG AA compliant
- **Alt Text**: Required for all images
- **Semantic HTML**: Proper heading hierarchy

## Performance

- **Minimal Dependencies**: No heavy frameworks
- **Lazy Loading**: Content loaded on demand
- **Optimized Assets**: Minified CSS/JS (production)
- **Caching**: Static assets cached by browser

## Security

- **CORS**: Configured via FastAPI middleware
- **Input Validation**: Client and server-side
- **XSS Prevention**: Template escaping
- **HTTPS**: Required for production

## Future Enhancements

- [ ] Session listing on dashboard
- [ ] Search and filter sessions
- [ ] Batch operations
- [ ] Export session data
- [ ] Drag-and-drop file upload
- [ ] Rich text editor for content
- [ ] Real-time collaboration
- [ ] Websocket for live updates
- [ ] Dark mode
- [ ] Internationalization (i18n)

## Troubleshooting

### UI not loading
- Check if FastAPI is running: `curl http://localhost:8001/health`
- Verify static files are mounted correctly
- Check browser console for errors

### API calls failing
- Verify API endpoints are accessible
- Check CORS configuration
- Inspect network tab in browser DevTools

### Styling issues
- Clear browser cache
- Check for CSS syntax errors
- Verify static files are being served

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn services.content_intake.main:app --reload --port 8001

# With debugging
uvicorn services.content_intake.main:app --reload --port 8001 --log-level debug
```

### Testing the UI

```bash
# Manual testing checklist:
- [ ] Create session with content blocks
- [ ] Create session with images
- [ ] Submit session for layout
- [ ] View session details
- [ ] Check artifacts
- [ ] Test error handling
- [ ] Test responsive design
```

## Production Deployment

### Optimizations

1. **Minify Assets**: Use CSS/JS minification
2. **Gzip Compression**: Enable in web server
3. **CDN**: Serve static assets from CDN
4. **Caching Headers**: Set appropriate cache policies

### Configuration

```python
# Production settings
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Monitoring

- Track page load times
- Monitor API response times
- Log user interactions
- Set up error reporting (e.g., Sentry)
