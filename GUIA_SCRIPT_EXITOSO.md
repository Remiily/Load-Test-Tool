# 🔥 Guía: Replicar el Stress del Script Exitoso

## ✅ Todo está integrado en el Web Panel

El sistema está **100% integrado** en el web panel. Puedes replicar el stress del script exitoso directamente desde la interfaz web.

## 🚀 Cómo Replicar el Stress del Script Exitoso

### Opción 1: Desde el Web Panel (RECOMENDADO)

#### Paso 1: Iniciar el Web Panel
```bash
python loadtest.py --web
```

#### Paso 2: Configurar Proxies
1. Ve a la pestaña **"Configuración"**
2. Expande la sección **"Configuración de Proxies (DEVASTADOR)"**
3. **Opción A**: Pega la lista de proxies en el textarea (desde `proxies.txt`)
4. **Opción B**: Carga el archivo `proxies.txt` usando el botón **"Cargar desde Archivo"**
5. Selecciona la estrategia de rotación: **Round-Robin** (recomendado)
6. Haz clic en **"Guardar Configuración"**

#### Paso 3: Hacer Fingerprint del Target
1. Ve a la pestaña **"Fingerprint"**
2. Ingresa el target (ej: `https://example.com`)
3. Haz clic en **"Ejecutar Fingerprint"**
4. Espera a que termine el análisis (3-5 segundos)

#### Paso 4: Lanzar Stress Recomendado
1. Después del fingerprint, verás el botón **"🚀 Lanzar Stress Recomendado"**
2. Este botón aplica automáticamente:
   - ✅ Herramienta recomendada según el fingerprint
   - ✅ Parámetros optimizados (workers, timeouts, etc.)
   - ✅ Proxies configurados
   - ✅ Bypass automático de CloudFront (si se detecta)
   - ✅ Múltiples endpoints y variaciones de URL
3. Haz clic en el botón y el stress comenzará automáticamente

#### Paso 5: Monitorear el Ataque
- **Dashboard**: Verás métricas en tiempo real (RPS, requests, errores, latencia)
- **Logs**: Errores y eventos importantes en tiempo real
- **Gráficos**: CPU, memoria, requests, errores, latencia

### Opción 2: Desde Línea de Comandos (Avanzado)

```bash
# Con proxies desde archivo
python loadtest.py -t https://example.com -d 300 -p EXTREME --proxy-file proxies.txt --proxy-rotation round-robin

# Con proxies desde string
python loadtest.py -t https://example.com -d 300 -p EXTREME --proxy-list "192.168.1.1:8080\n192.168.1.2:8080" --proxy-rotation round-robin
```

## 🎯 Características del Script Exitoso Implementadas

### ✅ 1. Sistema de Proxies
- **1000+ proxies** cargados desde `proxies.txt`
- **Rotación automática** (round-robin o random)
- **Manejo de proxies fallidos** (reintento después de 60s)
- **Distribución uniforme** entre workers

### ✅ 2. Bypass Automático de CloudFront
- **Detección automática** de CloudFront/CDN
- **Enumeración de subdominios** (similar a assetfinder)
- **Búsqueda de subdominios que bypassan CDN** (resuelven directamente a IP)
- **Auto-agregado a TARGET_VARIATIONS** para atacar directamente al origen

### ✅ 3. Optimizaciones Devastadoras
- **2-3x más workers** que el script exitoso (hasta 800 workers)
- **Multiplicadores dinámicos**:
  - Proxies: +50% efectividad
  - Múltiples endpoints: +30% efectividad
  - Múltiples IPs: +20% efectividad
- **Headers optimizados**: `Accept-Encoding: gzip, deflate, br` fijo
- **Connection keep-alive** explícito
- **Rotación agresiva** de endpoints, IPs y proxies

### ✅ 4. Múltiples Endpoints y Variaciones
- **Rotación automática** de URLs (round-robin)
- **Múltiples endpoints** descubiertos automáticamente
- **Variaciones de URL** con parámetros para evasión
- **Distribución de tráfico** entre múltiples rutas

### ✅ 5. Resolución DNS Múltiple
- **Resolución de múltiples IPs** para el mismo dominio
- **Rotación de IPs** para distribución de carga
- **Manejo de IPs dinámicas** y balanceadores
- **Host header correcto** en todas las requests

## 📊 Configuración Recomendada para Máxima Efectividad

### Desde el Web Panel:

1. **Target**: `https://example.com` (o el dominio que quieras atacar)
2. **Duración**: 300 segundos (5 minutos) o más
3. **Nivel de Potencia**: `EXTREME` o `GODMODE`
4. **Proxies**: Cargar desde `proxies.txt` (1000+ proxies)
5. **Rotación de Proxies**: `Round-Robin`
6. **Max Connections**: 50000 (ya configurado para Fortinet 40F)
7. **Max Threads**: 1000 (ya configurado)
8. **WAF Bypass**: Activado
9. **Stealth Mode**: Activado (opcional)
10. **Keep-Alive Pooling**: Activado
11. **Connection Warmup**: Activado
12. **Rate Adaptive**: Activado

### Parámetros del Script Exitoso Replicados:

- ✅ **Timeouts largos**: 30s connect, 60s read (para más sesiones)
- ✅ **Workers agresivos**: 2-3x más que el script exitoso
- ✅ **Headers fijos**: `Accept-Encoding: gzip, deflate, br` y `Connection: keep-alive`
- ✅ **Múltiples endpoints**: Rotación automática
- ✅ **Proxies rotativos**: Round-robin entre 1000+ proxies
- ✅ **Bypass CloudFront**: Automático si se detecta CDN
- ✅ **Múltiples IPs**: Resolución DNS múltiple y rotación

## 🔍 Verificación de Funcionamiento

### 1. Verificar Proxies Cargados
En el web panel, después de cargar proxies, deberías ver:
```
✅ 1000+ proxy(s) cargado(s) desde archivo: proxies.txt
```

### 2. Verificar Bypass de CloudFront
Si el target usa CloudFront, el fingerprint mostrará:
```
🛡️ CloudFront detectado
🔍 Buscando subdominios que bypassan CDN...
✅ Subdominios encontrados: backoffice-api.example.com, api-global.example.com
```

### 3. Verificar Configuración Final
Al iniciar el ataque, deberías ver:
```
⚙️ CONFIGURACIÓN FINAL
Target: https://example.com
Proxies cargados: 1000+ (round-robin)
Endpoints descubiertos: 10+
Max Connections: 50000
Max Threads: 1000
```

### 4. Verificar Sesiones en Fortinet
En tu Fortinet 40F, deberías ver:
- **Pico inicial**: 4000+ sesiones
- **Estabilización**: 15,000-20,000+ sesiones (con proxies y optimizaciones)
- **Distribución**: Tráfico distribuido entre múltiples IPs y proxies

## 🎯 Diferencia con el Script Exitoso

Nuestra herramienta es **MÁS DESTRUCTIVA** que el script exitoso:

1. **Más Workers**: 2-3x más workers (hasta 800 vs ~300 del script exitoso)
2. **Multiplicadores Dinámicos**: +50% con proxies, +30% con múltiples endpoints
3. **Bypass Automático**: Detecta y bypassa CloudFront automáticamente
4. **Manejo Inteligente**: Proxies fallidos se reintentan automáticamente
5. **Optimizaciones TCP**: Keep-alive, connection pooling, warmup
6. **Resolución DNS Múltiple**: Maneja IPs dinámicas y balanceadores

## ⚠️ Notas Importantes

1. **Proxies Funcionales**: Asegúrate de que los proxies en `proxies.txt` sean funcionales
2. **Permisos**: Verifica que tengas permisos para usar los proxies
3. **Recursos**: El sistema maneja automáticamente recursos, pero monitorea CPU/memoria
4. **Duración**: Para máxima efectividad, usa duraciones de 5+ minutos
5. **Fingerprint Primero**: Siempre haz fingerprint antes de atacar para optimización automática

## 🚨 Solución de Problemas

### Si no ves muchas sesiones:
1. Verifica que los proxies estén cargados (deberías ver "Proxies cargados: 1000+")
2. Verifica que el bypass de CloudFront funcionó (si aplica)
3. Aumenta la duración del ataque (más tiempo = más sesiones acumuladas)
4. Verifica que el nivel de potencia sea `EXTREME` o `GODMODE`

### Si hay muchos errores:
1. Verifica que los proxies sean funcionales
2. Verifica la conectividad al target
3. Revisa los logs en tiempo real en el web panel
4. Ajusta los timeouts si es necesario

### Si el sistema se cuelga:
1. El autothrottle debería prevenir esto automáticamente
2. Reduce el nivel de potencia si persiste
3. Verifica recursos del sistema (CPU/memoria)
4. Usa `--no-auto-throttle` solo si estás seguro de los recursos

## 📝 Resumen

✅ **Todo está integrado en el web panel**
✅ **Proxies funcionan desde la interfaz web**
✅ **Bypass de CloudFront es automático**
✅ **Optimizaciones del script exitoso están implementadas**
✅ **La herramienta es MÁS destructiva que el script exitoso**

**Para replicar el stress del script exitoso:**
1. Carga proxies desde `proxies.txt` en el web panel
2. Haz fingerprint del target
3. Haz clic en "🚀 Lanzar Stress Recomendado"
4. Monitorea en el dashboard

¡Listo para devastar! 🔥

