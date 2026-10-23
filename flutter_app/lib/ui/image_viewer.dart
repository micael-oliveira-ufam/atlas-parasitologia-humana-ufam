import 'package:flutter/material.dart';

import '../data/models.dart';
import 'theme.dart';
import 'widgets.dart';

/// Visualização ampliada em tela cheia: deslizar entre imagens, pinça/duplo toque para zoom,
/// ajuste de brilho/contraste (só na exibição; o arquivo não é alterado), crédito sempre visível.
class ImageViewerPage extends StatefulWidget {
  const ImageViewerPage({super.key, required this.images, required this.initialIndex, required this.title});

  final List<ImageItem> images;
  final int initialIndex;
  final String title;

  @override
  State<ImageViewerPage> createState() => _ImageViewerPageState();
}

class _ImageViewerPageState extends State<ImageViewerPage> {
  late final PageController _pc;
  late int _index;
  double _brightness = 0; // -1..1
  double _contrast = 1; // 0.5..2

  @override
  void initState() {
    super.initState();
    final n = widget.images.length;
    final i = widget.initialIndex;
    _index = i < 0 ? 0 : (i >= n ? n - 1 : i);
    _pc = PageController(initialPage: _index);
  }

  @override
  void dispose() {
    _pc.dispose();
    super.dispose();
  }

  List<double> get _matrix {
    final c = _contrast;
    final t = 128 * (1 - c) + _brightness * 255;
    return <double>[
      c, 0, 0, 0, t, //
      0, c, 0, 0, t,
      0, 0, c, 0, t,
      0, 0, 0, 1, 0,
    ];
  }

  void _showAdjust() {
    showModalBottomSheet<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheet) => Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Brilho e contraste', style: Theme.of(ctx).textTheme.titleMedium),
              const Text('Ajuste apenas de exibição; o arquivo original não é alterado.'),
              const SizedBox(height: 8),
              Text('Brilho: ${(_brightness * 100).round()}%'),
              Slider(
                value: _brightness,
                min: -0.5,
                max: 0.5,
                label: 'Brilho',
                onChanged: (v) {
                  setState(() => _brightness = v);
                  setSheet(() {});
                },
              ),
              Text('Contraste: ${(_contrast * 100).round()}%'),
              Slider(
                value: _contrast,
                min: 0.5,
                max: 2,
                label: 'Contraste',
                onChanged: (v) {
                  setState(() => _contrast = v);
                  setSheet(() {});
                },
              ),
              TextButton(
                onPressed: () {
                  setState(() {
                    _brightness = 0;
                    _contrast = 1;
                  });
                  setSheet(() {});
                },
                child: const Text('Restaurar'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showInfo(ImageItem im) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              PillWrap(pills: [
                Pill(im.typeLabel, tone: im.isMicrograph ? Tone.ok : Tone.warn),
                if (im.laminaLabel != null) Pill(im.laminaLabel!),
                if (im.confidenceLabel != null) Pill(im.confidenceLabel!),
                if (im.creditPending) Pill(im.credit == null ? 'Sem crédito' : 'Autoria a confirmar', tone: Tone.warn),
              ]),
              if (im.caption != null) ...[
                const SizedBox(height: 10),
                Text(im.caption!),
              ],
              const SizedBox(height: 10),
              Text('Autoria/crédito: ${im.creditLine}', style: const TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 6),
              Text('Arquivo: ${im.width > 0 ? im.width : '?'} × ${im.height > 0 ? im.height : '?'} px'
                  '${im.sourceFile != null ? ' · origem: ${im.sourceFile}' : ''}'),
              if (im.dateBasis != null) ...[
                const SizedBox(height: 6),
                Text('Base da data: ${im.dateBasis}'),
              ],
              if (im.hotspots.isNotEmpty) ...[
                const SizedBox(height: 6),
                Text('${im.hotspots.length} ponto(s) anotado(s): toque nos marcadores sobre a imagem.'),
              ],
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final n = widget.images.length;
    final im = widget.images[_index];
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.title, style: const TextStyle(fontSize: 16)),
            if (n > 1) Text('${_index + 1} de $n', style: const TextStyle(fontSize: 12, color: Colors.white70)),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.tune), tooltip: 'Brilho e contraste', onPressed: _showAdjust),
          IconButton(icon: const Icon(Icons.info_outline), tooltip: 'Informações e crédito', onPressed: () => _showInfo(im)),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: PageView.builder(
              controller: _pc,
              itemCount: n,
              onPageChanged: (i) => setState(() => _index = i),
              itemBuilder: (context, i) => ZoomableImage(
                key: ValueKey('${widget.images[i].id}#$i'),
                image: widget.images[i],
                matrix: _matrix,
              ),
            ),
          ),
          Container(
            width: double.infinity,
            color: Colors.black87,
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
            child: SafeArea(
              top: false,
              child: Text(
                'Autoria/crédito: ${im.creditLine}\nDuplo toque: zoom · pinça: ampliar',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ZoomableImage extends StatefulWidget {
  const ZoomableImage({super.key, required this.image, required this.matrix});

  final ImageItem image;
  final List<double> matrix;

  @override
  State<ZoomableImage> createState() => _ZoomableImageState();
}

class _ZoomableImageState extends State<ZoomableImage> {
  final TransformationController _tc = TransformationController();
  bool _zoomed = false;
  Size _size = Size.zero;

  @override
  void dispose() {
    _tc.dispose();
    super.dispose();
  }

  void _sync() {
    final z = _tc.value.getMaxScaleOnAxis() > 1.02;
    if (z != _zoomed) setState(() => _zoomed = z);
  }

  void _toggle() {
    if (_zoomed) {
      _tc.value = Matrix4.identity();
    } else {
      const s = 2.5;
      _tc.value = Matrix4.diagonal3Values(s, s, 1)
        ..setTranslationRaw(-_size.width * (s - 1) / 2, -_size.height * (s - 1) / 2, 0);
    }
    _sync();
  }

  @override
  Widget build(BuildContext context) {
    final im = widget.image;
    return LayoutBuilder(
      builder: (context, cons) {
        _size = cons.biggest;
        return GestureDetector(
          onDoubleTap: _toggle,
          child: InteractiveViewer(
            transformationController: _tc,
            minScale: 1,
            maxScale: 6,
            panEnabled: _zoomed,
            onInteractionEnd: (_) => _sync(),
            child: SizedBox(
              width: cons.maxWidth,
              height: cons.maxHeight,
              child: Center(
                child: AspectRatio(
                  aspectRatio: im.aspectRatio,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      ColorFiltered(
                        colorFilter: ColorFilter.matrix(widget.matrix),
                        child: Image.asset(
                          im.assetPath,
                          fit: BoxFit.fill,
                          filterQuality: FilterQuality.high,
                          semanticLabel: im.alt,
                          errorBuilder: (context, e, s) => const Center(child: Icon(Icons.broken_image_outlined, color: Colors.white54, size: 48)),
                        ),
                      ),
                      _HotspotLayer(hotspots: im.hotspots),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _HotspotLayer extends StatelessWidget {
  const _HotspotLayer({required this.hotspots});

  final List<Hotspot> hotspots;

  @override
  Widget build(BuildContext context) {
    if (hotspots.isEmpty) return const SizedBox.shrink();
    return LayoutBuilder(
      builder: (context, cons) {
        return Stack(
          children: [
            for (var i = 0; i < hotspots.length; i++)
              Positioned(
                left: hotspots[i].x / 100 * cons.maxWidth - 14,
                top: hotspots[i].y / 100 * cons.maxHeight - 14,
                child: Semantics(
                  button: true,
                  label: 'Ponto ${i + 1}: ${hotspots[i].title}',
                  child: GestureDetector(
                    onTap: () => showDialog<void>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: Text(hotspots[i].title),
                        content: Text(hotspots[i].description),
                        actions: [TextButton(onPressed: () => Navigator.of(ctx).pop(), child: const Text('Fechar'))],
                      ),
                    ),
                    child: Container(
                      width: 28,
                      height: 28,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: Colors.amber,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.black87, width: 2),
                      ),
                      child: Text('${i + 1}', style: const TextStyle(color: Colors.black, fontWeight: FontWeight.w700, fontSize: 12)),
                    ),
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}
